import logging
import asyncio
import shutil
import subprocess
from config import directory_to_watch, target_directory, python_executable, log_file, manage
from pathlib import Path

from watchgod import awatch, Change


logger = logging.getLogger('cam-archive')
logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)


# macos service definition: ~/Library/LaunchAgents/com.wgdnet.upload.agent.plist
# restart: In Aktivitätsanzeige stoppen, startet automatisch

async def main():
    async for changes in awatch(directory_to_watch):
        for change in changes:
            if change[0] == Change.added:
                filename = Path(str(change[1])).name
                source_file = Path(directory_to_watch) / filename
                target_file = Path(target_directory) / filename
                shutil.move(str(source_file), str(target_file))
                process = subprocess.run(  # noqa S603
                    [python_executable, manage, "video_consume", Path(filename).name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, check=False
                )
                msg = '{file} hochgeladen.'.format(file=Path(filename).name)
                logger.info(msg)
                msg = str(process.stderr)
                logger.error(msg)


loop = asyncio.run(main())
