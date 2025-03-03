from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from django.utils.dateformat import format
from django.urls import reverse
from django.utils.timezone import make_aware

from camera.models import Camera
from video.models import Video, get_name_from_file_name, get_camera_from_file_name, get_timestamp_from_file_name, \
    get_timestamp_from_string, create_thumbnail
from faker import Faker


class TestVideoModel(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.timestamp = make_aware(
            datetime(2025, 2, 3, 19, 38, 8)
        )
        self.camera = Camera.objects.create(
            name='Test',
            manufacturer=self.fake.word(),
            model=self.fake.word(),
        )
        self.name = f'{self.camera.name}__00_20250203193808.mp4'
        self.file_name = f'test_files/{self.camera.name}_00_20250203193808.mp4'
        self.video_file_name = self.file_name
        bytes = open(self.video_file_name, 'rb').read()
        self.video_file_content = BytesIO(bytes)
        self.video_file = SimpleUploadedFile(
            self.video_file_name,
            self.video_file_content.read(),
            content_type='video/mp4',
        )
        self.video = Video.objects.create(
            name='Test_00_20250203193808',
            camera=self.camera,
            timestamp=self.timestamp,
            file=self.video_file,
            thumbnail=None,
        )
        self.timestamp_as_string = format(self.video.timestamp, 'YmdHis')
        for i in range(1, 3):
            timestamp = timezone.now() + timedelta(hours=i)
            Video.objects.create(
                name=f'Test_00_{timestamp}',
                camera=self.camera,
                timestamp=timestamp,
                file=self.video_file,
                thumbnail=None,
            )

    def tearDown(self):
        Video.objects.all().delete()

    def test_string_representation(self):
        self.assertEqual(str(self.video), self.video.name)

    def test_absolute_url(self):
        self.assertEqual(
            self.video.get_absolute_url(),
            reverse('video:detail', kwargs={'pk': self.video.pk})
        )

    def test_get_name_from_file_name(self):
        self.assertEqual(
            self.video.name,
            get_name_from_file_name(self.file_name)
        )

    def test_get_camera_from_file_name(self):
        self.assertEqual(
            self.camera.name,
            get_camera_from_file_name(self.file_name)
        )

    def test_get_timestamp_from_file_name(self):
        self.assertEqual(
            self.timestamp_as_string,
            get_timestamp_from_file_name(self.file_name)
        )

    def test_get_timestamp_from_string(self):
        self.assertEqual(
            self.timestamp,
            get_timestamp_from_string(self.timestamp_as_string)
        )

    def test_auto_delete_file_on_delete(self):
        self.assertTrue(self.video.file and Path(self.video.file.path).is_file())
        self.video.delete()
        self.assertFalse(self.video.file and Path(self.video.file.path).is_file())

    def test_create_thumbnail(self):
        self.assertFalse(self.video.thumbnail)
        create_thumbnail(self.video)
        self.assertTrue(self.video.thumbnail)
        self.assertTrue(Path(self.video.thumbnail.path).is_file())

    def test_get_previous_by_timestamp(self):
        video = Video.objects.order_by('-timestamp').first()
        prev_video = video.get_previous_by_timestamp()
        self.assertIsInstance(prev_video, Video)
        self.assertTrue(prev_video.timestamp < video.timestamp)

    def test_get_next_by_timestamp(self):
        video = Video.objects.order_by('timestamp').first()
        next_video = video.get_next_by_timestamp()
        self.assertIsInstance(next_video, Video)
        self.assertTrue(next_video.timestamp > video.timestamp)
