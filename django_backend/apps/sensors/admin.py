from django.contrib import admin
from .models import SensorDevice, SensorReading, Threshold


@admin.register(SensorDevice)
class SensorDeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'name', 'location', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['device_id', 'name', 'location']


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['device', 'do', 'ph', 'temp', 'salinity', 'timestamp']
    list_filter = ['device']
    ordering = ['-timestamp']


@admin.register(Threshold)
class ThresholdAdmin(admin.ModelAdmin):
    list_display = [
        'do_min', 'do_max', 'ph_min', 'ph_max',
        'temp_min', 'temp_max', 'salinity_min', 'salinity_max',
        'updated_by', 'updated_at',
    ]
