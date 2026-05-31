from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/sensors/', include('apps.sensors.urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/audit/', include('apps.audit.urls')),
    path('api/shifts/', include('apps.shifts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
