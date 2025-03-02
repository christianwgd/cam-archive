import mimetypes
import os
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from camera.models import Camera
from video.models import Video, get_name_from_file_name, get_timestamp_from_file_name, \
    get_timestamp_from_string, create_thumbnail


class Command(BaseCommand):
    help = 'Import cam videos and set metadata'

    def handle(self, *args, **options):

        Video.objects.all().delete()
        camera = Camera.objects.get(name='Haustuer')

        # traverse root directory, and list directories as dirs and files as files
        home_dir = '/Users/christianwiegand/Desktop/2025/'
        for root, _dirs, files in os.walk(home_dir):
            for file_name in files:
                if mimetypes.guess_type(file_name)[0] not in ['video/mp4']:
                    continue
                video = Video(
                    name=get_name_from_file_name(file_name),
                    camera=camera,
                    timestamp=get_timestamp_from_string(
                        get_timestamp_from_file_name(file_name)
                    ),
                )
                full_path = Path(root) / file_name
                media_path = Path(settings.MEDIA_ROOT) / 'videos' / file_name
                video_path = Path('videos') / file_name
                shutil.copy(full_path, media_path)
                video.file.name = str(video_path)
                create_thumbnail(video)
                video.save()
