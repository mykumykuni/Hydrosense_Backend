from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from .models import SensorDevice, SensorReading, Threshold
from .serializers import (
    SensorDeviceSerializer, SensorReadingSerializer,
    SensorReadingWriteSerializer, ThresholdSerializer,
)
from .permissions import IsInternalService


class SensorDeviceViewSet(viewsets.ModelViewSet):
    queryset = SensorDevice.objects.all()
    serializer_class = SensorDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'device_id', 'location']
    ordering_fields = ['name', 'created_at']


class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.select_related('device').all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['device', 'device__device_id']
    ordering_fields = ['timestamp', 'received_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return SensorReadingWriteSerializer
        return SensorReadingSerializer

    def get_permissions(self):
        # POST /readings/ is reserved for the FastAPI ingestion service
        if self.action == 'create':
            return [IsInternalService()]
        return [permissions.IsAuthenticated()]


class ThresholdView(generics.RetrieveUpdateAPIView):
    """Singleton threshold config — always pk=1. Only admins may update."""
    serializer_class = ThresholdSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Threshold.get_instance()

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH'):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
