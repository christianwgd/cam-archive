from logging import getLogger

from django.conf import settings
from django.http import HttpResponse
from django.utils.formats import date_format
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_GET
from django.views.generic import ListView, DetailView
from django.utils import timezone

from video.models import Video, Ring

logger = getLogger('cam_archive')


class VideoListView(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'video/video_list.html'
    context_object_name = 'video_list'
    ordering = ['-timestamp']


class VideoDetailView(LoginRequiredMixin, DetailView):
    model = Video


@require_GET
def ring(request):  # pragma: no cover
    """
    Create a "ring" signal for the next uploaded video.
    """
    token = request.META.get('HTTP_AUTHORIZATION', None)
    api_token = getattr(settings, 'API_TOKEN', None)
    if not api_token or not token:
        return HttpResponse(status=403)
    if token != settings.RING_TOKEN:
        return HttpResponse(status=403)

    token = request.headers.get('X-API-Key', None)
    api_token = getattr(settings, 'API_TOKEN', None)
    if not api_token or not token:
        return HttpResponse(status=403)
    if token != api_token:
        return HttpResponse(status=403)

    timestamp = timezone.now()
    dt_str = date_format(timezone.now(), 'SHORT_DATETIME_FORMAT')
    msg = f"Get video thumbnail for timestamp {dt_str}"
    logger.info(msg)
    video = Video.objects.order_by('timestamp').filter(timestamp__lte=timestamp).last()
    msg = f"Video: {video}, Timestamp: {video.timestamp}, Thumbnail: {video.thumbnail}"
    logger.info(msg)
    Ring.objects.create()
    return HttpResponse(status=201)
