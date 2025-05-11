import requests
from logging import getLogger

from django.conf import settings
from django.utils.formats import date_format
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.views.generic import ListView, DetailView
from django.utils import dateparse

from video.models import Video


logger = getLogger('cam_archive')


class VideoListView(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'video/video_list.html'
    context_object_name = 'video_list'
    ordering = ['-timestamp']


class VideoDetailView(LoginRequiredMixin, DetailView):
    model = Video


@require_GET
def send_video_thumbnail(request, timestamp_iso):
    """
    Send video thumbnail to telegram channel
    """
    timestamp = dateparse.parse_datetime(timestamp_iso)
    dt_str = date_format(timestamp, 'SHORT_DATETIME_FORMAT')
    msg = f"Get video thumbnail for timestamp {dt_str}"
    logger.info(msg)
    video = Video.objects.order_by('timestamp').filter(timestamp__lte=timestamp).last()
    msg = f"Video: {video}, Timestamp: {video.timestamp}, Thumbnail: {video.thumbnail}"
    logger.info(msg)

    token = getattr(settings, 'TELEGRAM_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
    api_url = f'https://api.telegram.org/bot{token}/sendPhoto'
    if token is not None and chat_id is not None:
        message = ''
        params = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'markdown'
        }

        # Send the HTTP request
        with open(video.thumbnail.path, "rb") as image_file:
            response = requests.post(
                api_url, data=params,
                files={"photo": image_file},
                timeout=10
            )

        # Check if the request was successful
        if response.status_code == 200:
            msg = f"Message sent successfully! Response: {response.json()}"
            logger.info(msg)
        else:
            msg = f"Failed to send message. Status code: {response.status_code}, Response: {response.text}"
            logger.error(msg)

    else:
        logger.error('Telegram token or chat id not found.')

    return redirect(request.META.get('HTTP_REFERER', '/'))
