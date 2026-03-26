import asyncio
import logging
import subprocess
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


import importlib
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock, patch


class ConsumerTests(IsolatedAsyncioTestCase):

    def setUp(self):
        sys.modules.pop("consumer.cam_file_consumer", None)
        self.consumer = importlib.import_module("consumer.cam_file_consumer")

    async def test_wait_for_file_stability_returns_true_when_file_stable(self):
        file_path = Path("test_files/tmp/video.mp4")

        times = iter([0, 1, 2, 3, 4, 5, 6])

        class FakeLoop:
            def time(self):
                return next(times)

        with patch.object(self.consumer.asyncio, "get_running_loop", return_value=FakeLoop()), patch.object(
            self.consumer.asyncio,
            "sleep",
            AsyncMock(),
        ):
            result = await self.consumer.wait_for_file_stability(
                file_path,
                quiet_period=2,
                poll_interval=1,
                max_wait=10,
            )

        self.assertTrue(result)

    async def test_wait_for_file_stability_returns_false_on_timeout(self):
        file_path = Path("test_files/tmp/video.mp4")

        times = iter([0, 1, 2, 3, 4, 5])

        class FakeLoop:
            def time(self):
                return next(times)

        with patch.object(self.consumer.asyncio, "get_running_loop", return_value=FakeLoop()), patch.object(
            self.consumer.asyncio,
            "sleep",
            AsyncMock(),
        ):
            result = await self.consumer.wait_for_file_stability(
                file_path,
                quiet_period=10,
                poll_interval=1,
                max_wait=4,
            )

        self.assertFalse(result)

    async def test_process_change_ignores_non_added_changes(self):
        wait_for_file_stability = AsyncMock()
        create_subprocess_exec = AsyncMock()

        with patch.object(self.consumer, "wait_for_file_stability", wait_for_file_stability), patch.object(
            self.consumer.asyncio,
            "create_subprocess_exec",
            create_subprocess_exec,
        ):
            change = (self.consumer.Change.modified, Path("test_files/tmp/ignored.mp4"))
            await self.consumer.process_change(change)

        wait_for_file_stability.assert_not_awaited()
        create_subprocess_exec.assert_not_awaited()

    async def test_process_change_starts_subprocess_when_file_is_stable(self):
        fake_process = SimpleNamespace(
            returncode=0,
            communicate=AsyncMock(return_value=(b"ok", b"")),
        )
        wait_for_file_stability = AsyncMock(return_value=True)
        create_subprocess_exec = AsyncMock(return_value=fake_process)

        with patch.object(self.consumer, "wait_for_file_stability", wait_for_file_stability), patch.object(
            self.consumer.asyncio,
            "create_subprocess_exec",
            create_subprocess_exec,
        ):
            change = (self.consumer.Change.added, Path("test_files/tmp/Test_00_20250203193808.mp4"))
            await self.consumer.process_change(change)

        wait_for_file_stability.assert_awaited_once()
        create_subprocess_exec.assert_awaited_once_with(
            self.consumer.python_executable,
            self.consumer.manage,
            "video_consume",
            "Test_00_20250203193808.mp4",
            stdout=self.consumer.subprocess.PIPE,
            stderr=self.consumer.subprocess.PIPE,
        )
        fake_process.communicate.assert_awaited_once()

    async def test_process_change_logs_error_when_subprocess_fails(self):
        fake_process = SimpleNamespace(
            returncode=1,
            communicate=AsyncMock(return_value=(b"", b"boom")),
        )
        wait_for_file_stability = AsyncMock(return_value=True)
        create_subprocess_exec = AsyncMock(return_value=fake_process)
        logger_error = Mock()

        with patch.object(self.consumer, "wait_for_file_stability", wait_for_file_stability), patch.object(
            self.consumer.asyncio,
            "create_subprocess_exec",
            create_subprocess_exec,
        ), patch.object(self.consumer.logger, "error", logger_error):
            change = (self.consumer.Change.added, Path("test_files/tmp/broken.mp4"))
            await self.consumer.process_change(change)

        logger_error.assert_any_call("Error processing broken.mp4")
        logger_error.assert_any_call("boom")

    async def test_main_handles_exception_during_processing(self):
        async def fake_awatch(_directory):
            yield {(self.consumer.Change.added, Path("test_files/tmp/file.mp4"))}

        async def boom(_change):
            raise RuntimeError("boom")

        logger_exception = Mock()

        with patch.object(self.consumer, "awatch", fake_awatch), patch.object(
            self.consumer,
            "directory_to_watch",
            "test_files/tmp/watch",
        ), patch.object(self.consumer, "process_change", boom), patch.object(
            self.consumer.logger,
            "exception",
            logger_exception,
        ):
            task = self.consumer.asyncio.create_task(self.consumer.main())
            await self.consumer.asyncio.sleep(0)
            task.cancel()

            with self.assertRaises(self.consumer.asyncio.CancelledError):
                await task

        logger_exception.assert_called_once()


if __name__ == "__main__":
    main_cli()
