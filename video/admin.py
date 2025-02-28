from django.contrib import admin

from video.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):

    list_display = ['name', 'file', 'timestamp']
    date_hierarchy = 'timestamp'
    search_fields = ['name']
