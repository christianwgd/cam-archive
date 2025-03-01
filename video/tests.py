from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware

from camera.models import Camera
from video.models import Video
from faker import Faker


class TestVideoModel(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.camera = Camera.objects.create(
            name=self.fake.word(),
            manufacturer=self.fake.word(),
            model=self.fake.word(),
        )
        self.video = Video.objects.create(
            name=self.fake.word(),
            camera=self.camera,
            timestamp=make_aware(self.fake.date_time_this_decade(before_now=True, after_now=False)),
            file=self.fake.url(),
            thumbnail=self.fake.url(),
        )

    def test_string_representation(self):
        self.assertEqual(str(self.video), self.video.name)

    def test_absolute_url(self):
        self.assertEqual(
            self.video.get_absolute_url(),
            reverse('video:detail', kwargs={'pk': self.video.pk})
        )
