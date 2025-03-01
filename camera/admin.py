from django.contrib import admin

from camera.models import Camera


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):

    list_display = ['name', 'manufacturer', 'model']
    search_fields = ['name']
