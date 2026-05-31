from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.sensors.models import SensorReading
from apps.alerts.models import Alert

GROUP_NAME = 'hydrosense'


def _broadcast(event: dict):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(GROUP_NAME, event)


@receiver(post_save, sender=SensorReading)
def on_sensor_reading_saved(sender, instance, created, **kwargs):
    if not created:
        return
    _broadcast({
        'type': 'sensor.reading',
        'data': {
            'id': instance.id,
            'device_id': instance.device.device_id if instance.device else None,
            'do': instance.do,
            'ph': instance.ph,
            'temp': instance.temp,
            'salinity': instance.salinity,
            'ts': int(instance.received_at.timestamp() * 1000) if instance.received_at else None,
        },
    })


@receiver(post_save, sender=Alert)
def on_alert_saved(sender, instance, created, **kwargs):
    update_fields = set(kwargs.get('update_fields') or [])

    if created:
        event_type = 'alert.new'
    elif 'resolved' in update_fields:
        event_type = 'alert.resolved'
    else:
        return

    _broadcast({
        'type': event_type,
        'data': {
            'id': instance.id,
            'uid': instance.uid,
            'severity': instance.severity,
            'title': instance.title,
            'message': instance.message,
            'source': instance.source,
            'resolved': instance.resolved,
            'ts': int(instance.created_at.timestamp() * 1000) if instance.created_at else None,
        },
    })
