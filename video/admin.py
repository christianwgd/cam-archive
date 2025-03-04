from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from video.models import Video, create_thumbnail


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):

    list_display = ['name', 'file', 'timestamp']
    date_hierarchy = 'timestamp'
    search_fields = ['name']
    actions = ['generate_thumbnail']

    @admin.action(description=_('Generate thumbnail for video'))
    def generate_thumbnail(self, request, queryset):
        for obj in queryset:
            create_thumbnail(obj)
            obj.save()
            messages.success(request, _('Successfully generated thumbnail for %s"') % obj)
