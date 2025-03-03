from django.views.generic import ListView, DetailView

from camera.models import Camera


class CameraListView(ListView):
    model = Camera
    template_name = 'camera/camera_list.html'
    context_object_name = 'camera_list'
    ordering = ['name']


class CameraDetailView(DetailView):
    model = Camera
