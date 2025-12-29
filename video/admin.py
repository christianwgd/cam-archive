from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from video.models import Video, Ring


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):

    list_display = ['name', 'timestamp', 'duration']
    list_filter = ['camera']
    date_hierarchy = 'timestamp'
    search_fields = ['name']
    actions = ['generate_thumbnail', 'set_duration']

    @admin.action(description=_('Generate thumbnail for video'))
    def generate_thumbnail(self, request, queryset):
        for obj in queryset:
            obj.set_thumbnail()
            messages.success(request, _('Successfully generated thumbnail for %s"') % obj)

    @admin.action(description=_('Set video duration'))
    def set_duration(self, request, queryset):
        for obj in queryset:
            if obj.file is not None:
                obj.set_duration()
                messages.success(request, _('Successfully set duration for %s"') % obj)


@admin.register(Ring)
class RingAdmin(admin.ModelAdmin):
    list_display = ['timestamp']
    date_hierarchy = 'timestamp'
