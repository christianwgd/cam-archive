import django_filters

from video.models import Video


class VideoFilter(django_filters.FilterSet):
    class Meta:
        model = Video
        fields = ["camera", "timestamp"]


    camera = django_filters.AllValuesFilter(field_name="camera__name")
    timestamp = django_filters.DateRangeFilter()
