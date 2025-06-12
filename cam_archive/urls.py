from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView


admin.autodiscover()
admin.site.site_header = _('Cam Archive')
admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/signup/', RedirectView.as_view(url='/', permanent=True)),
    path('accounts/', include('allauth.urls')),
    path('video/', include('video.urls')),
    path('camera/', include('camera.urls')),

    # Startseite
    path('', RedirectView.as_view(url="video/list/"), name='home'),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon/favicon.ico')),
]
if settings.DEBUG:  # pragma: no cover
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
