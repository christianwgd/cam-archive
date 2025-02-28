import os
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from video.models import Video, get_name_from_file_name, get_camera_from_file_name, get_timestamp_from_file_name, \
    get_timestamp_from_string


class Command(BaseCommand):
    help = 'Import cam videos and set metadata'

    def handle(self, *args, **options):

        Video.objects.all().delete()

        # traverse root directory, and list directories as dirs and files as files
        home_dir = '/Users/christianwiegand/Desktop/2025/'
        for root, _dirs, files in os.walk(home_dir):
            for file_name in files:
                video = Video(
                    name=get_name_from_file_name(file_name),
                    camera=get_camera_from_file_name(file_name),
                    timestamp=get_timestamp_from_string(
                        get_timestamp_from_file_name(file_name)
                    ),
                )
                full_path = Path(root) / file_name
                media_path = Path(settings.MEDIA_ROOT) / 'videos' / file_name
                video_path = Path('videos') / file_name
                shutil.copy(full_path, media_path)
                video.file.name = str(video_path)
                video.save()
