from rest_framework import serializers
from .models import ShiftLog


class ShiftLogSerializer(serializers.ModelSerializer):
    ts = serializers.IntegerField(source='ts', read_only=True)

    class Meta:
        model = ShiftLog
        fields = ['id', 'uid', 'operator', 'operator_email', 'operator_name', 'note', 'ts', 'created_at']
        read_only_fields = ['id', 'uid', 'operator', 'operator_email', 'operator_name', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        profile = getattr(user, 'profile', None)
        validated_data['operator'] = user
        validated_data['operator_email'] = user.email
        validated_data['operator_name'] = (
            profile.display_name if profile and profile.display_name else user.email
        )
        return super().create(validated_data)
