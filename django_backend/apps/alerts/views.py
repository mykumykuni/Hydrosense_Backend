from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['severity', 'resolved', 'source']
    search_fields = ['title', 'message', 'source']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Alert.objects.prefetch_related('read_by').all()

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        alert = self.get_object()
        alert.read_by.add(request.user)
        return Response({'detail': 'Marked as read.'})

    @action(detail=True, methods=['post'], url_path='resolve',
            permission_classes=[permissions.IsAdminUser])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.resolved = True
        alert.save(update_fields=['resolved'])
        return Response(AlertSerializer(alert, context={'request': request}).data)

    @action(detail=False, methods=['delete'], url_path='clear-all',
            permission_classes=[permissions.IsAdminUser])
    def clear_all(self, request):
        Alert.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
