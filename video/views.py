from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from video.models import Video


class VideoListView(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'video/video_list.html'
    context_object_name = 'video_list'
    ordering = ['-timestamp']


class VideoDetailView(LoginRequiredMixin, DetailView):
    model = Video
