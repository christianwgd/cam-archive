from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from camera.models import Camera


class CameraListView(LoginRequiredMixin, ListView):
    model = Camera
    template_name = 'camera/camera_list.html'
    context_object_name = 'camera_list'
    ordering = ['name']


class CameraDetailView(LoginRequiredMixin, DetailView):
    model = Camera
