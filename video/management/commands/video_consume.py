import mimetypes
from logging import getLogger
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from camera.models import Camera
from video.models import Video, get_name_from_file_name, get_timestamp_from_file_name, \
    get_timestamp_from_string, create_thumbnail, get_camera_from_file_name, get_duration

logger = getLogger('cam_archive')


class Command(BaseCommand):
    help = 'Import cam videos and set metadata'

    def add_arguments(self, parser):
        parser.add_argument("file_name", type=str)

    def handle(self, *args, **options):
        if not options['file_name']:
            error_msg = "No file name provided"
            logger.error(error_msg)
            raise CommandError(error_msg)

        msg = f"Processing {options['file_name']}"
        logger.info(msg)
        self.style.SUCCESS(msg)

        file_name = options['file_name']
        msg ='Video file found "%s"' % file_name
        logger.info(msg)
        self.style.SUCCESS(msg)

        camera, created = Camera.objects.get_or_create(name=get_camera_from_file_name(file_name))
        if created:
            msg = 'Camera created "%s"' % camera
        else:
            msg = 'Camera found "%s"' % camera
        logger.info(msg)
        self.style.SUCCESS(msg)

        if mimetypes.guess_type(file_name)[0] not in ['video/mp4']:
            msg = 'Video file "%s"' % file_name
            logger.error(msg)
            self.style.ERROR(msg)

        video = Video(
            name=get_name_from_file_name(file_name),
            camera=camera,
            timestamp=get_timestamp_from_string(
                get_timestamp_from_file_name(file_name)
            ),
        )
        video_path = Path('videos') / file_name
        video.file.name = str(video_path)
        create_thumbnail(video)
        video.duration = get_duration(video)
        video.save()
