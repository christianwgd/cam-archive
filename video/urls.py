from django.urls import path, register_converter

from video import views
from video.converters import DateConverter

app_name = "video"


register_converter(DateConverter, "date")

urlpatterns = [
    path("list/", views.VideoListView.as_view(), name="list"),
    path("list/<date:date>/", views.VideoListView.as_view(), name="list"),
    path("detail/<int:pk>/", views.VideoDetailView.as_view(), name="detail"),
    path("delete/<int:pk>/", views.VideoDeleteView.as_view(), name="delete"),
    path("ring/", views.ring, name="ring"),
]
