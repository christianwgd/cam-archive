import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _

from camera.models import Camera


def get_name_from_file_name(file_name):
    return file_name.split('/')[-1].split('.')[0]


def get_camera_from_file_name(file_name):
    return get_name_from_file_name(file_name).split('_')[0]


def get_timestamp_from_file_name(file_name):
    return get_name_from_file_name(file_name).split('_')[-1]


def get_timestamp_from_string(file_name):
    return make_aware(
        datetime.strptime(
            get_timestamp_from_file_name(file_name), '%Y%m%d%H%M%S'
        )
    )


class Video(models.Model):

    class Meta:
        verbose_name = _('Video')
        verbose_name_plural = _('Videos')
        ordering = ['-timestamp']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('video:detail', kwargs={'pk': self.pk})

    name = models.CharField(
        verbose_name=_('name'), max_length=255
    )
    camera = models.ForeignKey(
        Camera, on_delete=models.CASCADE, verbose_name=_('camera')
    )
    file = models.FileField(
        verbose_name=_('video file'), upload_to='videos/'
    )
    thumbnail = models.FileField(
        verbose_name=_('thumbnail'), upload_to='thumbs/', null=True, blank=True,
    )
    timestamp = models.DateTimeField(
        verbose_name=_('timestamp')
    )
    duration = models.SmallIntegerField(
        verbose_name=_('duration'), default=0, null=True, blank=True,
        help_text=_('Duration of the video in seconds')
    )


def get_duration(instance):
    if instance.file:
        ffmpeg_path = getattr(settings, 'FFMPEG_BIN', None)
        if not ffmpeg_path:
            ffprobe = shutil.which('ffprobe')
        else:
            ffprobe = Path(ffmpeg_path) / 'ffprobe'
        result = subprocess.check_output([  # noqa: S603
            ffprobe,
            "-v",  "error", "-select_streams", "v:0",
            "-show_entries", "stream=duration", "-of",
            "default=noprint_wrappers=1:nokey=1",
            instance.file.path
        ])
        return int(result.decode().split('.')[0])
    return 0


def create_thumbnail(instance):
    """
    Creates thumbnail file for video file
    and sets it to corresponding `Video` object.
    """
    if instance.file:
        ffmpeg_path = getattr(settings, 'FFMPEG_BIN', None)
        if not ffmpeg_path:
            ffmpeg = shutil.which('ffmpeg')
        else:
            ffmpeg = Path(ffmpeg_path) / 'ffmpeg'
        thumb_name = f'thumbs/thumb-{get_name_from_file_name(instance.file.name)}.jpg'
        thumb_path = Path(settings.MEDIA_ROOT) / thumb_name
        if instance.duration:
            if instance.duration > 5:
                sec = 5
            else:
                sec = instance.duration
        else:
            sec = 3
        subprocess.call([  # noqa: S603
            ffmpeg,
            '-y', '-i',
            instance.file.path,
            '-ss', f'00:00:0{sec}',
            '-vframes', '1',
            thumb_path
        ])
        instance.thumbnail.name = str(thumb_name)


@receiver(models.signals.post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Video` object is deleted.
    """
    if instance.file and Path(instance.file.path).is_file():
        Path.unlink(instance.file.path)
    if instance.thumbnail and Path(instance.thumbnail.path).is_file():
        Path.unlink(instance.thumbnail.path)
