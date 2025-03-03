from django.urls import path

from camera import views

app_name = 'camera'

urlpatterns = [
    path('list/', views.CameraListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.CameraDetailView.as_view(), name='detail'),
]
