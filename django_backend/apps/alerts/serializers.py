from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    read = serializers.SerializerMethodField()
    ts = serializers.IntegerField(source='ts', read_only=True)

    class Meta:
        model = Alert
        fields = ['id', 'uid', 'severity', 'title', 'message', 'source', 'read', 'resolved', 'ts', 'created_at']
        read_only_fields = ['id', 'uid', 'created_at']

    def get_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.read_by.filter(pk=request.user.pk).exists()
        return False
