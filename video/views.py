from logging import getLogger

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET
from django.views.generic import DeleteView, DetailView
from django_filters.views import FilterView

from video.filters import VideoFilter
from video.models import Ring, Video

logger = getLogger("cam_archive")


class VideoListView(LoginRequiredMixin, FilterView):
    model = Video
    template_name = "video/video_list.html"
    context_object_name = "video_list"
    ordering = ["-timestamp"]
    filterset_class = VideoFilter

    def get_queryset(self):
        query_date = self.kwargs.get("date", now().date())
        return Video.objects.filter(timestamp__date=query_date)

    def get_context_data(self, **kwargs):
        query_date = self.kwargs.get("date", now().date())
        context = super().get_context_data(**kwargs)
        context["query_date"] = query_date

        days_present = Video.objects.all().annotate(
            ts_date=TruncDay("timestamp"),
        ).values(
            "ts_date",
        ).annotate(
            date=Count("ts_date"),
        ).order_by("-ts_date")

        days = [value["ts_date"].date() for value in days_present]
        context["days"] = days
        for i in range(len(days)):
            if days[i] == query_date:
                context["prev_date"] = days[i+1] if i+1 < len(days) else None
                context["next_date"] = days[i-1] if i-1 >= 0 else None
                break

        return context


class VideoDetailView(LoginRequiredMixin, DetailView):
    model = Video


class VideoDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Video
    success_url = reverse_lazy("video:list")
    success_message = _("Video deleted")


@require_GET
def ring(request):
    """
    Create a "ring" signal for the next uploaded video.
    """
    token = request.headers.get("X-API-Key", None)
    api_token = getattr(settings, "API_TOKEN", None)
    if not api_token or not token:
        return HttpResponse(status=403)
    if token != api_token:
        return HttpResponse(status=403)
    msg = "Request video thumbnail by creatin a new ring signal"
    logger.info(msg)
    ring = Ring.objects.create()
    msg = f"Ring signal created at {ring.timestamp}"
    return HttpResponse(status=201)
