import os
import sys
import asyncio
import logging
import subprocess
from logging.handlers import RotatingFileHandler
from pathlib import Path

from django.conf import settings
from watchfiles import Change, awatch

if not settings.configured:
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    )
    from cam_archive import settings

directory_to_watch = getattr(settings, "WATCH_DIR", "media/videos")
log_file = getattr(settings, "CONSUMER_LOG_FILE", "log/cam_consumer.log")
manage = getattr(settings, "MANAGE", "manage.py")
python_executable = getattr(settings, "PYTHON_EXECUTABLE", "python")
print(directory_to_watch, log_file, manage, python_executable)

logger = logging.getLogger("cam-archive")
handler = RotatingFileHandler(log_file, maxBytes=2000000, backupCount=5)
logging.basicConfig(
    handlers=[handler],
    encoding="utf-8",
    format="%(levelname)s %(asctime)s %(message)s",
    level=logging.INFO,
)


async def wait_for_file_stability(
    file_path: Path,
    quiet_period: int = 10,
    poll_interval: int = 2,
    max_wait: int = 300,
) -> bool:
    last_change = asyncio.get_running_loop().time()
    previous_snapshot = None
    deadline = last_change + max_wait

    while asyncio.get_running_loop().time() < deadline:
        if not file_path.exists():  # noqa: ASYNC240
            previous_snapshot = None
            last_change = asyncio.get_running_loop().time()
            await asyncio.sleep(poll_interval)
            continue

        current_snapshot = (file_path.stat().st_size, file_path.stat().st_mtime)  # noqa: ASYNC240
        if current_snapshot != previous_snapshot:
            previous_snapshot = current_snapshot
            last_change = asyncio.get_running_loop().time()
        elif asyncio.get_running_loop().time() - last_change >= quiet_period:
            return True

        await asyncio.sleep(poll_interval)

    return False


async def process_change(change) -> None:
    msg = f"Processing change: {change}"
    logger.info(msg)

    if change[0] != Change.added:
        return

    file_path = Path(str(change[1]))
    filename = file_path.name
    msg = f"File created: {filename}, waiting for upload to complete."
    logger.info(msg)

    if not await wait_for_file_stability(file_path):
        logger.error("File did not become stable in time: %s", filename)
        return

    logger.info("Starting video consuming process...")
    process = await asyncio.create_subprocess_exec(
        python_executable,
        manage,
        "video_consume",
        filename,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        msg = f"Error processing {filename}"
        logger.error(msg)
        if stderr:
            logger.error(stderr.decode("utf-8", errors="replace"))
        return

    msg = f"{filename} uploaded."
    logger.info(msg)
    if stdout:
        logger.info(stdout.decode("utf-8", errors="replace"))


async def main() -> None:
    async for changes in awatch(directory_to_watch):
        for change in changes:
            try:
                await process_change(change)
            except Exception:
                logger.exception("Unexpected error while processing file change")


def main_cli() -> None:
    asyncio.run(main())

if __name__ == "__main__":
    main_cli()
