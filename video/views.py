from django.views.generic import ListView, DetailView

from video.models import Video


class VideoListView(ListView):
    model = Video
    template_name = 'video/video_list.html'
    context_object_name = 'video_list'
    ordering = ['-timestamp']


class VideoDetailView(DetailView):
    model = Video
