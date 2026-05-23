# Add this to your main urls.py (the one with urlpatterns)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your existing URL patterns ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
