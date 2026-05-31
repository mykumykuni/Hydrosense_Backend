from rest_framework.permissions import BasePermission
from django.conf import settings


class IsInternalService(BasePermission):
    """Allows access only to internal services that supply the correct API key.
    Used for FastAPI → Django sensor data ingestion."""

    def has_permission(self, request, view):
        api_key = request.headers.get('X-Api-Key', '')
        return bool(api_key and api_key == settings.INTERNAL_API_KEY)
