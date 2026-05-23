from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def debug_cloudinary(request):
    storage = getattr(settings, 'CLOUDINARY_STORAGE', {})
    cloudinary_url = getattr(settings, 'CLOUDINARY_URL', 'NOT SET')
    return JsonResponse({
        'CLOUDINARY_URL': cloudinary_url,
        'CLOUD_NAME': storage.get('CLOUD_NAME', 'NOT SET'),
        'API_KEY': storage.get('API_KEY', 'NOT SET'),
        'API_SECRET_FIRST10': storage.get('API_SECRET', 'NOT SET')[:10],
        'DEFAULT_FILE_STORAGE': settings.DEFAULT_FILE_STORAGE,
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('debug-cloudinary/', debug_cloudinary),
    path('', include('albums.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
