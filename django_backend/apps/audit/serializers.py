from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    ts = serializers.IntegerField(source='ts', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'uid', 'action', 'actor_email', 'detail', 'ts', 'created_at']
        read_only_fields = ['id', 'uid', 'created_at']
