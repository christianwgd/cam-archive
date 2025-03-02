import mimetypes
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from camera.models import Camera
from video.models import Video, get_name_from_file_name, get_timestamp_from_file_name, \
    get_timestamp_from_string, create_thumbnail, get_camera_from_file_name


class Command(BaseCommand):
    help = 'Import cam videos and set metadata'

    def add_arguments(self, parser):
        parser.add_argument("file_name", type=str)

    def handle(self, *args, **options):
        if not options['file_name']:
            error_msg = "No file name provided"
            raise CommandError(error_msg)

        file_name = options['file_name']
        self.style.SUCCESS('Video file found "%s"' % file_name)

        camera, created = Camera.objects.get_or_create(name=get_camera_from_file_name(file_name))
        if created:
            self.style.SUCCESS('Camera created "%s"' % camera)
        else:
            self.style.SUCCESS('Camera used "%s"' % camera)

        if mimetypes.guess_type(file_name)[0] not in ['video/mp4']:
            self.style.ERROR('File is not a videw file "%s"' % file_name)

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
        video.save()
