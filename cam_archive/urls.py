from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from two_factor.urls import urlpatterns as tf_urls


admin.site.site_header = _('Cam Archive')

urlpatterns = [
    path('', include(tf_urls)),
    path('admin/', admin.site.urls),
    path('video/', include('video.urls')),
    path('camera/', include('camera.urls')),

    # Startseite
    path('', RedirectView.as_view(url="video/list/"), name='home'),
]
if settings.DEBUG:  # pragma: no cover
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
