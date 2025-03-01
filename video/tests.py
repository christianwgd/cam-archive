from django.test import TestCase
from django.urls import reverse
from video.models import Video
from faker import Faker


class TestVideoModel(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.video = Video.objects.create(
            name=self.fake.word(),
            timestamp=self.fake.date_time_this_decade(before_now=True, after_now=False),
            video=self.fake.url(),
            source=self.fake.url(),
        )

    def test_string_representation(self):
        video = Video(name=self.fake.word())
        self.assertEqual(str(video), video.name)

    def test_absolute_url(self):
        video = Video(pk=self.fake.random_int(min=1, max=1000))
        self.assertEqual(video.get_absolute_url(), reverse('video:detail', kwargs={'pk': video.pk}))

    def test_verbose_name_plural(self):
        self.assertEqual(str(Video._meta.verbose_name_plural), "Videos")

    def test_ordering(self):
        video1 = Video(timestamp=self.fake.date_time_this_decade(before_now=True, after_now=False))
        video2 = Video(timestamp=self.fake.date_time_this_decade(before_now=False, after_now=True))
        self.assertTrue(video1.timestamp < video2.timestamp)
