import asyncio
import logging
import subprocess
from time import sleep

from config import directory_to_watch, target_directory, python_executable, log_file, manage
from pathlib import Path

from watchgod import awatch, Change


logger = logging.getLogger('cam-archive')
logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)


async def main():
    async for changes in awatch(directory_to_watch):
        for change in changes:
            if change[0] == Change.added:
                # sleep(5)  # Give the file time to be written completely
                filename = Path(str(change[1])).name
                # source_file = Path(directory_to_watch) / filename
                # target_file = Path(target_directory) / filename
                # msg = f"Copying {source_file} to {target_file}"
                # logger.info(msg)
                # shutil.copy2(source_file, target_file)
                # msg = f"Copied {source_file} to {target_file}"
                # logger.info(msg)
                # msg = '{file} copied.'.format(file=Path(filename).name)
                # logger.info(msg)
                # Path(source_file).unlink()
                # msg = f"Deleted {source_file}"
                # logger.info(msg)

                process = subprocess.run(  # noqa S603
                    [python_executable, manage, "video_consume", Path(filename).name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, check=False
                )
                msg = '{file} uploaded.'.format(file=Path(filename).name)
                logger.info(msg)
                msg = str(process.stderr)
                logger.error(msg)


loop = asyncio.run(main())
