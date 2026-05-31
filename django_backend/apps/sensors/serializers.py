from rest_framework import serializers
from .models import SensorDevice, SensorReading, Threshold


class SensorDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorDevice
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SensorReadingSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    ts = serializers.SerializerMethodField()

    class Meta:
        model = SensorReading
        fields = '__all__'
        read_only_fields = ['received_at']

    def get_ts(self, obj):
        return int(obj.received_at.timestamp() * 1000)


class SensorReadingWriteSerializer(serializers.ModelSerializer):
    """Used by the FastAPI ingestion endpoint — resolves device by device_id string."""
    device_id = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = SensorReading
        fields = [
            'device_id', 'do', 'ph', 'temp', 'salinity', 'timestamp', 'raw_payload',
        ]

    def validate_device_id(self, value):
        if not value:
            return None
        try:
            return SensorDevice.objects.get(device_id=value)
        except SensorDevice.DoesNotExist:
            raise serializers.ValidationError(f"Device '{value}' not found.")

    def create(self, validated_data):
        device = validated_data.pop('device_id', None)
        return SensorReading.objects.create(device=device, **validated_data)


class ThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Threshold
        fields = '__all__'
        read_only_fields = ['updated_at']
