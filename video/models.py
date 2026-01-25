import shutil
import subprocess
from datetime import datetime
from decimal import Decimal
from logging import getLogger
from pathlib import Path

import requests
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.translation import gettext_lazy as _

from camera.models import Camera

logger = getLogger("cam_archive")


def get_name_from_file_name(file_name):
    return file_name.split("/")[-1].split(".")[0]


def get_camera_from_file_name(file_name):
    return get_name_from_file_name(file_name).split("_")[0]


def get_timestamp_from_file_name(file_name):
    return get_name_from_file_name(file_name).split("_")[-1]


def get_timestamp_from_string(file_name):
    dt = datetime.strptime(
        get_timestamp_from_file_name(file_name), "%Y%m%d%H%M%S",
    ).replace(tzinfo=timezone.get_current_timezone())
    return dt.astimezone(timezone.get_current_timezone())


class Video(models.Model):

    name = models.CharField(
        verbose_name=_("name"), max_length=255,
    )
    camera = models.ForeignKey(
        Camera, on_delete=models.CASCADE, verbose_name=_("camera"),
    )
    file = models.FileField(
        verbose_name=_("video file"), upload_to="videos/",
    )
    thumbnail = models.FileField(
        verbose_name=_("thumbnail"), upload_to="thumbs/", null=True, blank=True,
    )
    timestamp = models.DateTimeField(
        verbose_name=_("timestamp"),
    )
    duration = models.SmallIntegerField(
        verbose_name=_("duration"), default=0, null=True, blank=True,
        help_text=_("Duration of the video in seconds"),
    )
    telegram = models.BooleanField(
        verbose_name=_("Sent to telegram"), default=False,
        help_text=_("Thumbnail sent to telegram"),
    )

    class Meta:
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")
        ordering = ["-timestamp"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("video:detail", kwargs={"pk": self.pk})


    def set_duration(self):
        if self.file:
            ffmpeg_path = getattr(settings, "FFMPEG_BIN", None)
            ffprobe = shutil.which("ffprobe") if not ffmpeg_path else Path(ffmpeg_path) / "ffprobe"
            result = subprocess.check_output([  # noqa: S603
                ffprobe,
                "-v", "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                self.file.path,
            ])
            self.duration = round(Decimal(result.strip().decode("utf-8")))
            self.save()

    def set_thumbnail(self):
        if self.file:
            ffmpeg_path = getattr(settings, "FFMPEG_BIN", None)
            ffmpeg = shutil.which("ffmpeg") if not ffmpeg_path else Path(ffmpeg_path) / "ffmpeg"
            thumb_name = f"thumbs/thumb-{get_name_from_file_name(self.file.name)}.jpg"
            thumb_path = Path(settings.MEDIA_ROOT) / thumb_name
            sec = (min(self.duration, 5)) if self.duration else 5
            subprocess.call([  # noqa: S603
                ffmpeg,
                "-ss", f"00:00:0{sec}.000",
                "-y", "-i",
                self.file.path,
                "-vframes", "1",
                thumb_path,
            ])
            self.thumbnail.name = str(thumb_name)
            self.save()

    def check_send_thumbnail(self):  # pragma: no cover
        ring_signals = Ring.objects.all()
        msg = f"Checking for ring signals: {ring_signals.count()}"
        if ring_signals.count() > 0 and self.thumbnail:
            ring = ring_signals.first()
            msg = f"Sending thumbnail to Telegram for ring at {ring.timestamp}"
            logger.info(msg)
            # Delete all Rings after sending the thumbnail, so no
            # rings are left over from double pressing bell button
            ring_signals.delete()
            msg = f"Deleted, should be 0: {Ring.objects.all().count()}"
            token = getattr(settings, "TELEGRAM_TOKEN", None)
            chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)
            api_url = f"https://api.telegram.org/bot{token}/sendPhoto"
            if token is not None and chat_id is not None:
                message = ""
                params = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "markdown",
                }

                # Send the HTTP request
                with Path(self.thumbnail.path).open("rb") as image_file:
                    response = requests.post(
                        api_url, data=params,
                        files={"photo": image_file},
                        timeout=10,
                    )

                # Check if the request was successful
                if response.status_code == 200:
                    msg = f"Message sent successfully! Response: {response.json()}"
                    logger.info(msg)
                    self.telegram = True
                    self.save()
                else:
                    msg = f"Failed to send message. Status code: {response.status_code}, Response: {response.text}"
                    logger.error(msg)

            else:
                logger.error("Telegram token or chat id not found.")


class Ring(models.Model):

    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("timestamp"),
    )

    class Meta:
        verbose_name = _("Ring")
        verbose_name_plural = _("Rings")
        ordering = ["timestamp"]

    def __str__(self):
        return formats.date_format(
            self.timestamp,
            format="DATETIME_FORMAT",
            use_l10n=True,
        )


@receiver(models.signals.post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):  # noqa: ARG001
    """
    Deletes file from filesystem
    when corresponding `Video` object is deleted.
    """
    if instance.file and Path(instance.file.path).is_file():
        Path.unlink(instance.file.path)
    if instance.thumbnail and Path(instance.thumbnail.path).is_file():
        Path.unlink(instance.thumbnail.path)
