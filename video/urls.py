from django.urls import path

from video import views

app_name = 'video'

urlpatterns = [
    path('list/', views.VideoListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.VideoDetailView.as_view(), name='detail'),
    path('send_thumbnail/<str:timestamp_iso>/', views.send_video_thumbnail, name='send_thumbnail'),
]
