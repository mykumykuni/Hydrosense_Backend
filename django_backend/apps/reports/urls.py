from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, ReportReplyViewSet

router = DefaultRouter()
router.register('', ReportViewSet, basename='report')
router.register('replies', ReportReplyViewSet, basename='report-reply')

urlpatterns = [
    path('', include(router.urls)),
]
