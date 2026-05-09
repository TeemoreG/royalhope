from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('consultations.urls')),
]

# Serve static files during development and on Render
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # For production (Render)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
