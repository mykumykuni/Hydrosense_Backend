from rest_framework import viewsets, permissions
from .models import Report, ReportReply
from .serializers import ReportSerializer, ReportReplySerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.select_related('submitted_by').prefetch_related('replies').all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['type', 'priority', 'status', 'submitted_by']
    search_fields = ['subject', 'message']
    ordering_fields = ['created_at', 'priority', 'status']


class ReportReplyViewSet(viewsets.ModelViewSet):
    queryset = ReportReply.objects.select_related('report', 'author').all()
    serializer_class = ReportReplySerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['report']
    ordering_fields = ['created_at']
