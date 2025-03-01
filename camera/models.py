from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Camera(models.Model):

    class Meta:
        verbose_name = _('Camera')
        verbose_name_plural = _('Cameras')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('camera:detail', kwargs={'pk': self.pk})

    name = models.CharField(
        verbose_name=_('name'), max_length=255
    )
    manufacturer = models.CharField(
        verbose_name=_('manufacturer'), max_length=255
    )
    model = models.CharField(
        verbose_name=_('model'), max_length=255
    )

