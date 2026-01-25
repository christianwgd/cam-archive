import shutil
from datetime import datetime, timedelta
from io import BytesIO, StringIO
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib import auth
from django.contrib.admin import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import CommandError, call_command
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import dateformat, formats, timezone
from faker import Faker

from camera.models import Camera
from video.admin import VideoAdmin
from video.models import (
    Ring,
    Video,
    get_camera_from_file_name,
    get_name_from_file_name,
    get_timestamp_from_file_name,
    get_timestamp_from_string,
)

User = auth.get_user_model()


class TestVideoModel(TestCase):

    def setUp(self):
        self.fake = Faker("de_DE")
        self.timestamp = datetime(
            2025, 2, 3, 19, 38, 8,
            tzinfo=timezone.get_current_timezone(),
        )
        self.camera = Camera.objects.create(
            name="Test",
            manufacturer=self.fake.word(),
            model=self.fake.word(),
        )
        self.name = f"{self.camera.name}__00_20250203193808.mp4"
        self.file_name = f"test_files/{self.camera.name}_00_20250203193808.mp4"
        self.video_file_name = self.file_name
        with Path(self.video_file_name).open("rb") as f:
            content = f.read()
            self.video_file_content = BytesIO(content)
            self.video_file = SimpleUploadedFile(
                self.video_file_name,
                self.video_file_content.read(),
                content_type="video/mp4",
            )
            self.video = Video.objects.create(
                name="Test_00_20250203193808",
                camera=self.camera,
                timestamp=self.timestamp,
                file=self.video_file,
                thumbnail=None,
            )
            self.timestamp_as_string = dateformat.format(
                self.video.timestamp, "YmdHis",
            )
            for i in range(1, 3):
                timestamp = timezone.now() + timedelta(hours=i)
                Video.objects.create(
                    name=f"Test_00_{timestamp}",
                    camera=self.camera,
                    timestamp=timestamp,
                    file=self.video_file,
                    thumbnail=None,
                )
            f.close()

    def tearDown(self):
        Video.objects.all().delete()

    def test_string_representation(self):
        self.assertEqual(str(self.video), self.video.name)

    def test_absolute_url(self):
        self.assertEqual(
            self.video.get_absolute_url(),
            reverse("video:detail", kwargs={"pk": self.video.pk}),
        )

    def test_get_name_from_file_name(self):
        self.assertEqual(
            self.video.name,
            get_name_from_file_name(self.file_name),
        )

    def test_get_camera_from_file_name(self):
        self.assertEqual(
            self.camera.name,
            get_camera_from_file_name(self.file_name),
        )

    def test_get_timestamp_from_file_name(self):
        self.assertEqual(
            self.timestamp_as_string,
            get_timestamp_from_file_name(self.file_name),
        )

    def test_get_timestamp_from_string(self):
        self.assertEqual(
            self.timestamp,
            get_timestamp_from_string(self.timestamp_as_string),
        )

    def test_auto_delete_file_on_delete(self):
        self.assertTrue(self.video.file and Path(self.video.file.path).is_file())
        self.video.delete()
        self.assertFalse(self.video.file and Path(self.video.file.path).is_file())

    def test_video_set_thumbnail(self):
        self.assertFalse(self.video.thumbnail)
        self.video.set_thumbnail()
        self.video.refresh_from_db()
        self.assertTrue(self.video.thumbnail)
        self.assertTrue(Path(self.video.thumbnail.path).is_file())

    def test_video_set_duration(self):
        self.assertEqual(0, self.video.duration)
        self.video.set_duration()
        self.video.refresh_from_db()
        self.assertIsInstance(self.video.duration, int)
        self.assertTrue(self.video.duration > 0)

    def test_get_previous_by_timestamp(self):
        video = Video.objects.order_by("-timestamp").first()
        prev_video = video.get_previous_by_timestamp()
        self.assertIsInstance(prev_video, Video)
        self.assertTrue(prev_video.timestamp < video.timestamp)

    def test_get_next_by_timestamp(self):
        video = Video.objects.order_by("timestamp").first()
        next_video = video.get_next_by_timestamp()
        self.assertIsInstance(next_video, Video)
        self.assertTrue(next_video.timestamp > video.timestamp)


class VideoAdminActionTests(TestVideoModel):

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = "session"
        self.request._messages = FallbackStorage(self.request)  # noqa: SLF001
        self.video_admin = VideoAdmin(Video, AdminSite())

    def test_action_generate_thumbnail_duration_none(self):
        self.assertTrue(self.video.thumbnail.name is None)
        queryset = Video.objects.filter(pk=self.video.pk)
        self.video_admin.generate_thumbnail(self.request, queryset)
        self.assertTrue(queryset.exists())
        self.video.refresh_from_db()
        self.assertFalse(self.video.thumbnail.name is None)

    def test_action_generate_thumbnail_duration_gt_5(self):
        self.video.duration = 6
        self.video.save()
        self.assertTrue(self.video.thumbnail.name is None)
        queryset = Video.objects.filter(pk=self.video.pk)
        self.video_admin.generate_thumbnail(self.request, queryset)
        self.assertTrue(queryset.exists())
        self.video.refresh_from_db()
        self.assertFalse(self.video.thumbnail.name is None)

    def test_action_generate_thumbnail_duration_lt_5(self):
        self.video.duration = 4
        self.video.save()
        self.assertTrue(self.video.thumbnail.name is None)
        queryset = Video.objects.filter(pk=self.video.pk)
        self.video_admin.generate_thumbnail(self.request, queryset)
        self.assertTrue(queryset.exists())
        self.video.refresh_from_db()
        self.assertFalse(self.video.thumbnail.name is None)

    def test_action_set_duration(self):
        self.assertTrue(self.video.duration == 0)
        queryset = Video.objects.filter(pk=self.video.pk)
        self.video_admin.set_duration(self.request, queryset)
        self.assertTrue(queryset.exists())
        self.video.refresh_from_db()
        self.assertFalse(self.video.duration == 0)

    def test_action_set_duration_no_video(self):
        self.video.file = None
        self.video.save()
        self.assertTrue(self.video.duration == 0)
        queryset = Video.objects.filter(pk=self.video.pk)
        self.video_admin.set_duration(self.request, queryset)
        self.assertTrue(queryset.exists())
        self.video.refresh_from_db()
        self.assertTrue(self.video.duration == 0)


class CommandsTestCase(TestCase):

    def tearDown(self):
        Video.objects.all().delete()

    def call_command(self, command, *args, **kwargs):
        out = StringIO()
        call_command(
            command,
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_video_import(self):
        self.call_command(
            "video_import",
            "test_files/",
        )
        videos = Video.objects.all()
        self.assertEqual(videos.count(), 1)
        video = videos.first()
        self.assertEqual(video.file.name, "videos/Test_00_20250203193808.mp4")
        self.assertEqual(video.camera, Camera.objects.get(name="Test"))

    def test_video_consume(self):
        shutil.copy(
            "test_files/Test_00_20250203193808.mp4",
            "media/videos/Test_00_20250203193808.mp4",
        )
        self.call_command(
            "video_consume",
            "Test_00_20250203193808.mp4",
        )
        videos = Video.objects.all()
        self.assertEqual(videos.count(), 1)
        video = videos.filter(name="Test_00_20250203193808").first()
        self.assertEqual(video.file.name, "videos/Test_00_20250203193808.mp4")
        self.assertEqual(video.camera, Camera.objects.get(name="Test"))

    def test_video_consume_no_file(self):
        with pytest.raises(CommandError):
            self.call_command("video_consume")

    def test_video_delete_no_stale(self):
        self.fake = Faker("de_DE")
        self.timestamp = datetime(
            2025, 2, 3, 19, 38, 8,
            tzinfo=timezone.get_current_timezone(),
        )
        self.camera = Camera.objects.create(
            name="Test",
            manufacturer=self.fake.word(),
            model=self.fake.word(),
        )
        self.name = f"{self.camera.name}__00_20250203193808.mp4"
        self.file_name = f"test_files/{self.camera.name}_00_20250203193808.mp4"
        self.video_file_name = self.file_name
        with Path(self.video_file_name).open("rb") as f:
            content = f.read()
            self.video_file_content = BytesIO(content)
            self.video_file = SimpleUploadedFile(
                self.video_file_name,
                self.video_file_content.read(),
                content_type="video/mp4",
            )
            self.timestamp_as_string = format(self.timestamp, "YmdHis")
            for i in range(1, 3):
                timestamp = timezone.now() + timedelta(hours=i)
                Video.objects.create(
                    name=f"Test_00_{timestamp}",
                    camera=self.camera,
                    timestamp=timestamp,
                    file=self.video_file,
                    thumbnail=None,
                )
            out = self.call_command("video_delete")
            self.assertIn("Deleted 0 videos", out)
            f.close()

    def test_video_delete(self):
        self.fake = Faker("de_DE")
        self.timestamp = timezone.now() - timedelta(days=15)
        self.camera = Camera.objects.create(
            name="Test",
            manufacturer=self.fake.word(),
            model=self.fake.word(),
        )
        self.name = f"{self.camera.name}__00_20250203193808.mp4"
        self.file_name = f"test_files/{self.camera.name}_00_20250203193808.mp4"
        self.video_file_name = self.file_name
        with Path(self.video_file_name).open("rb") as f:
            content = f.read()
            self.video_file_content = BytesIO(content)
            self.video_file = SimpleUploadedFile(
                self.video_file_name,
                self.video_file_content.read(),
                content_type="video/mp4",
            )
            self.timestamp_as_string = format(self.timestamp, "YmdHis")
            for i in range(3):
                timestamp = self.timestamp - timedelta(hours=i)
                Video.objects.create(
                    name=f"Test_00_{timestamp}",
                    camera=self.camera,
                    timestamp=timestamp,
                    file=self.video_file,
                    thumbnail=None,
                )
            out = self.call_command("video_delete")
            self.assertIn("Deleted 3 videos", out)
            f.close()


class RingTestCase(TestCase):

    def setUp(self):
        self.ring = Ring.objects.create()

    def tearDown(self):
        self.ring.delete()

    def test_ring_repr(self):
        self.assertEqual(
            str(self.ring),
            formats.date_format(
                self.ring.timestamp,
                format="DATETIME_FORMAT",
                use_l10n=True,
            ),
        )

    def test_ring_view_function(self):
        headers = {
            "Content-Type" : "application/json",
            "x-api-key": settings.API_TOKEN,
        }
        response = self.client.get(reverse("video:ring"), headers=headers)
        self.assertEqual(response.status_code, 201)
        rings = Ring.objects.all()
        # There should be 2 ring instances, the one created in setUp
        # and the one created from view function call above
        self.assertEqual(rings.count(), 2)
