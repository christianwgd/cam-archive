from django.test import TestCase
from django.utils.dateformat import format
from django.urls import reverse
from django.utils.timezone import make_aware

from camera.models import Camera
from video.models import Video, get_name_from_file_name, get_camera_from_file_name, get_timestamp_from_file_name, \
    get_timestamp_from_string
from faker import Faker


class TestVideoModel(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.timestamp = make_aware(
            self.fake.date_time_this_year(
                before_now=True, after_now=False
            ).replace(microsecond=0)
        )
        self.camera = Camera.objects.create(
            name=self.fake.word(),
            manufacturer=self.fake.word(),
            model=self.fake.word(),
        )
        self.name = f'{self.camera}_{self.timestamp.strftime("%Y%m%d%H%M%S")}'
        self.file_name = f'{self.name}.mp4'
        self.video = Video.objects.create(
            name=self.name,
            camera=self.camera,
            timestamp=self.timestamp,
            file=f'videos/{self.file_name}',
            thumbnail=self.fake.url(),
        )
        self.timestamp_as_string = format(self.video.timestamp, 'YmdHis')

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
