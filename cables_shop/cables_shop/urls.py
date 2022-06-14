from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

from . import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.extend([path('__debug__/', include(debug_toolbar.urls))])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
