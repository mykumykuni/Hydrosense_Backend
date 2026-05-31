from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShiftLogViewSet

router = DefaultRouter()
router.register('', ShiftLogViewSet, basename='shift-log')

urlpatterns = [
    path('', include(router.urls)),
]
