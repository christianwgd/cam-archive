import importlib
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def consumer_module():
    sys.modules.pop("consumer.cam_file_consumer", None)
    return importlib.import_module("consumer.cam_file_consumer")


@pytest.mark.asyncio
async def test_wait_for_file_stability_returns_true_when_file_stable(
    consumer_module, monkeypatch, tmp_path,
):
    file_path = tmp_path / "video.mp4"
    file_path.write_text("ready")

    times = iter([0, 1, 2, 3, 4, 5, 6])

    class FakeLoop:
        @staticmethod
        def time():
            return next(times)

    monkeypatch.setattr(
        consumer_module.asyncio,
        "get_running_loop",
        lambda: FakeLoop(),  # noqa: PLW0108
    )
    monkeypatch.setattr(consumer_module.asyncio, "sleep", AsyncMock())

    result = await consumer_module.wait_for_file_stability(
        file_path,
        quiet_period=2,
        poll_interval=1,
        max_wait=10,
    )

    assert result is True  # noqa: S101


@pytest.mark.asyncio
async def test_wait_for_file_stability_returns_false_on_timeout(
    consumer_module, monkeypatch, tmp_path,
):
    file_path = tmp_path / "video.mp4"
    file_path.write_text("changing")

    times = iter([0, 1, 2, 3, 4, 5])

    class FakeLoop:
        @staticmethod
        def time():
            return next(times)

    monkeypatch.setattr(
        consumer_module.asyncio,
        "get_running_loop",
        lambda: FakeLoop(),  # noqa: PLW0108
    )
    monkeypatch.setattr(consumer_module.asyncio, "sleep", AsyncMock())

    result = await consumer_module.wait_for_file_stability(
        file_path,
        quiet_period=10,
        poll_interval=1,
        max_wait=4,
    )

    assert result is False  # noqa: S101


@pytest.mark.asyncio
async def test_process_change_ignores_non_added_changes(consumer_module, monkeypatch):
    wait_for_file_stability = AsyncMock()
    create_subprocess_exec = AsyncMock()

    monkeypatch.setattr(consumer_module, "wait_for_file_stability", wait_for_file_stability)
    monkeypatch.setattr(consumer_module.asyncio, "create_subprocess_exec", create_subprocess_exec)

    change = (consumer_module.Change.modified, Path("test_files/tmp/ignored.mp4"))
    await consumer_module.process_change(change)

    wait_for_file_stability.assert_not_awaited()
    create_subprocess_exec.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_change_starts_subprocess_when_file_is_stable(
    consumer_module, monkeypatch,
):
    fake_process = SimpleNamespace(
        returncode=0,
        communicate=AsyncMock(return_value=(b"ok", b"")),
    )

    wait_for_file_stability = AsyncMock(return_value=True)
    create_subprocess_exec = AsyncMock(return_value=fake_process)

    monkeypatch.setattr(consumer_module, "wait_for_file_stability", wait_for_file_stability)
    monkeypatch.setattr(consumer_module.asyncio, "create_subprocess_exec", create_subprocess_exec)

    change = (consumer_module.Change.added, Path("test_files/tmp/Test_00_20250203193808.mp4"))
    await consumer_module.process_change(change)

    wait_for_file_stability.assert_awaited_once()
    create_subprocess_exec.assert_awaited_once_with(
        consumer_module.python_executable,
        consumer_module.manage,
        "video_consume",
        "Test_00_20250203193808.mp4",
        stdout=consumer_module.subprocess.PIPE,
        stderr=consumer_module.subprocess.PIPE,
    )
    fake_process.communicate.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_change_logs_error_when_subprocess_fails(
    consumer_module, monkeypatch,
):
    fake_process = SimpleNamespace(
        returncode=1,
        communicate=AsyncMock(return_value=(b"", b"boom")),
    )
    wait_for_file_stability = AsyncMock(return_value=True)
    create_subprocess_exec = AsyncMock(return_value=fake_process)

    logger_error = Mock()
    monkeypatch.setattr(consumer_module, "wait_for_file_stability", wait_for_file_stability)
    monkeypatch.setattr(consumer_module.asyncio, "create_subprocess_exec", create_subprocess_exec)
    monkeypatch.setattr(consumer_module.logger, "error", logger_error)

    change = (consumer_module.Change.added, Path("test_files/tmp/broken.mp4"))
    await consumer_module.process_change(change)

    logger_error.assert_any_call("Error processing broken.mp4")
    logger_error.assert_any_call("boom")


@pytest.mark.asyncio
async def test_main_logs_error_when_processing_change_raises_exception(consumer_module, monkeypatch):
    async def fake_awatch(_directory):
        yield {(consumer_module.Change.added, Path("test_files/tmp/file.mp4"))}

    async def boom(_change):
        error_msg = "boom"
        raise RuntimeError(error_msg)

    logger_exception = Mock()

    monkeypatch.setattr(consumer_module, "awatch", fake_awatch)
    monkeypatch.setattr(consumer_module, "directory_to_watch", "test_files/tmp/watch")
    monkeypatch.setattr(consumer_module, "process_change", boom)
    monkeypatch.setattr(consumer_module.logger, "exception", logger_exception)

    await consumer_module.main()

    logger_exception.assert_called_once()
