import asyncio
import logging
import subprocess
from logging.handlers import RotatingFileHandler

from config import directory_to_watch, python_executable, log_file, manage
from pathlib import Path

from watchgod import awatch, Change


logger = logging.getLogger('cam-archive')
handler = RotatingFileHandler(log_file, maxBytes=2000000, backupCount=5)
logging.basicConfig(
    handlers=[handler],
    encoding='utf-8',
    format='%(levelname)s %(asctime)s %(message)s',
    level=logging.INFO,
)


async def main():
    async for changes in awatch(directory_to_watch):
        for change in changes:
            msg = f'Processing change: {change}'
            logger.info(msg)
            if change[0] == Change.added:
                filename = Path(str(change[1])).name
                msg = f'Processing filename: {filename}'
                logger.info(msg)
                process = subprocess.run(  # noqa S603
                    [python_executable, manage, "video_consume", Path(filename).name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, check=False
                )
                if process.returncode != 0:
                    msg = 'Error processing {file}'.format(file=Path(filename).name)
                    logger.error(msg)
                    msg = str(process.stderr)
                    logger.error(msg)
                else:
                    msg = '{file} uploaded.'.format(file=Path(filename).name)
                    logger.info(msg)


loop = asyncio.run(main())
