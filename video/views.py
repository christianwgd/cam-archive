from logging import getLogger

from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_GET
from django.views.generic import ListView, DetailView

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
def ring(request):
    """
    Create a "ring" signal for the next uploaded video.
    """
    token = request.headers.get('X-API-Key', None)
    api_token = getattr(settings, 'API_TOKEN', None)
    if not api_token or not token:
        return HttpResponse(status=403)
    if token != api_token:
        return HttpResponse(status=403)
    msg = "Request video thumbnail by creatin a new ring signal"
    logger.info(msg)
    ring = Ring.objects.create()
    msg = f"Ring signal created at {ring.timestamp}"
    return HttpResponse(status=201)
