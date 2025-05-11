from django.urls import path

from video import views

app_name = 'video'

urlpatterns = [
    path('list/', views.VideoListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.VideoDetailView.as_view(), name='detail'),
    path('thumbnail/', views.send_video_thumbnail, name='thumbnail'),
]
