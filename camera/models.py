from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Camera(models.Model):

    name = models.CharField(
        verbose_name=_("name"), max_length=255,
    )
    manufacturer = models.CharField(
        verbose_name=_("manufacturer"), max_length=255, null=True, blank=True,
    )
    model = models.CharField(
        verbose_name=_("model"), max_length=255, null=True, blank=True,
    )
    image = models.ImageField(
        verbose_name=_("Image"), upload_to="camera/", null=True, blank=True,
    )

    class Meta:
        verbose_name = _("Camera")
        verbose_name_plural = _("Cameras")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("camera:detail", kwargs={"pk": self.pk})
