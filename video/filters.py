import django_filters

from video.models import Video


class VideoFilter(django_filters.FilterSet):
    class Meta:
        model = Video
        fields = [
            "camera",
        ]

    camera = django_filters.AllValuesFilter(field_name="camera__name")
