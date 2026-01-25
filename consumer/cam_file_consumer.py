import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import directory_to_watch, log_file, manage, python_executable
from watchfiles import Change, awatch

logger = logging.getLogger("cam-archive")
handler = RotatingFileHandler(log_file, maxBytes=2000000, backupCount=5)
logging.basicConfig(
    handlers=[handler],
    encoding="utf-8",
    format="%(levelname)s %(asctime)s %(message)s",
    level=logging.INFO,
)


async def main():
    async for changes in awatch(directory_to_watch):
        for change in changes:
            msg = f"Processing change: {change}"
            logger.info(msg)
            if change[0] == Change.added:
                filename = Path(str(change[1])).name
                msg = f"File created: {filename}, waiting 40 sec to complete upload."
                logger.info(msg)
                await asyncio.sleep(40)
                process = asyncio.create_subprocess_exec(
                    python_executable, manage, "video_consume", Path(filename).name,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()
                if process.returncode != 0:
                    msg = f"Error processing {Path(filename).name}"
                    logger.error(msg)
                    msg = str(stderr.decode(), "utf-8")
                    logger.error(msg)
                else:
                    msg = f"{Path(filename).name} uploaded."
                    logger.info(msg)
                    msg = str(stdout.decode(), "utf-8")
                    logger.info(msg)


loop = asyncio.run(main())
