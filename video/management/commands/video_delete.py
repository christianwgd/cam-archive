from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from video.models import Video


class Command(BaseCommand):
    help = 'Delete old videos'

    def handle(self, *args, **options):
        days_keep_videos = getattr(settings, 'DAYS_KEEP_VIDEOS', 14)
        keep_date = timezone.now() - timedelta(days=days_keep_videos)
        old_videos = Video.objects.filter(timestamp__date__lt=keep_date.date())
        count = old_videos.count()
        old_videos.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} videos'))


