from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CameraConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "camera"
    verbose_name = _("Camera")
