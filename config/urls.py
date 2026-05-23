from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
import base64
import cloudinary as cld
import cloudinary.uploader


def debug_cloudinary(request):
    cfg = cld.config()

    tiny_png = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    )

    try:
        result = cloudinary.uploader.upload(
            tiny_png,
            resource_type='image',
            public_id='test_connection_ping',
            overwrite=True,
        )
        upload_test = 'SUCCESS — ' + result.get('secure_url', 'no url returned')
    except Exception as e:
        upload_test = 'FAILED — ' + str(e)

    return JsonResponse({
        'cloud_name': cfg.cloud_name,
        'api_key': cfg.api_key,
        'api_secret_first6': (cfg.api_secret or '')[:6],
        'upload_test': upload_test,
        'DEFAULT_FILE_STORAGE': settings.DEFAULT_FILE_STORAGE,
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('albums.urls')),
    path('debug-cloudinary/', debug_cloudinary),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
