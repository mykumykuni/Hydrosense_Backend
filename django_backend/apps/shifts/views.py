from rest_framework import viewsets, permissions
from .models import ShiftLog
from .serializers import ShiftLogSerializer


class ShiftLogViewSet(viewsets.ModelViewSet):
    queryset = ShiftLog.objects.select_related('operator').all()
    serializer_class = ShiftLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['operator', 'operator_email']
    search_fields = ['note', 'operator_email', 'operator_name']
    ordering_fields = ['created_at']

    def get_permissions(self):
        # Only operators (and admins) can create shift logs; only admins can delete
        if self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
