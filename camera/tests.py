from django.test import TestCase
from django.urls import reverse
from faker import Faker

from camera.models import Camera


class TestCameraModel(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.camera = Camera.objects.create(
            name='Test',
            manufacturer=self.fake.word(),
            model=self.fake.word(),
        )

    def test_string_representation(self):
        self.assertEqual(str(self.camera), self.camera.name)

    def test_absolute_url(self):
        self.assertEqual(
            self.camera.get_absolute_url(),
            reverse('camera:detail', kwargs={'pk': self.camera.pk})
        )

