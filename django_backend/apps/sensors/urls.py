from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SensorDeviceViewSet, SensorReadingViewSet, ThresholdView

router = DefaultRouter()
router.register('devices', SensorDeviceViewSet, basename='sensor-device')
router.register('readings', SensorReadingViewSet, basename='sensor-reading')

urlpatterns = [
    path('', include(router.urls)),
    path('thresholds/', ThresholdView.as_view(), name='threshold'),
]
