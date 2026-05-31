from django.db import models
from django.conf import settings


class SensorDevice(models.Model):
    """Registry of physical IoT sensor devices."""
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sensor_devices'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.device_id})'


class SensorReading(models.Model):
    """Time-series water quality snapshot received from an IoT device."""
    device = models.ForeignKey(
        SensorDevice, on_delete=models.SET_NULL, null=True, blank=True, related_name='readings'
    )
    # Water quality parameters
    do = models.FloatField(null=True, blank=True)        # Dissolved oxygen (mg/L)
    ph = models.FloatField(null=True, blank=True)         # pH
    temp = models.FloatField(null=True, blank=True)       # Temperature (°C)
    salinity = models.FloatField(null=True, blank=True)   # Salinity (ppt)
    timestamp = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)
    raw_payload = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'sensor_readings'
        ordering = ['-timestamp']

    def __str__(self):
        return f'Reading @ {self.timestamp} — DO:{self.do} pH:{self.ph} T:{self.temp}'


class Threshold(models.Model):
    """Global water quality thresholds — singleton (pk=1). Admin-configurable.

    3-level severity system:  Safe → Warning → Critical
      Levels are defined per parameter using *_min / *_max (Safe boundary)
      and *_critical_min / *_critical_max (Critical boundary).

      Safe     : value within [min, max]
      Warning  : value in [critical_min, min) or (max, critical_max]
      Critical : value < critical_min  OR  value > critical_max

    Defaults:
      DO       : safe 4.0–9.0 mg/L,  critical <1.4 or >12.0
      pH       : safe 6.0–8.0,       critical <4.0 or >10.0
      Temp     : safe 28.0–32.0 °C,  critical <25.0 or >35.0
      Salinity : safe 28.0–33.0 ppt, critical <20.0 or >40.0
    """
    # Dissolved oxygen (mg/L)  — Safe: 4.0–9.0
    do_min = models.FloatField(default=4.0)
    do_max = models.FloatField(default=9.0)
    do_critical_min = models.FloatField(default=1.4)
    do_critical_max = models.FloatField(default=12.0)
    # pH  — Safe: 6.0–8.0
    ph_min = models.FloatField(default=6.0)
    ph_max = models.FloatField(default=8.0)
    ph_critical_min = models.FloatField(default=4.0)
    ph_critical_max = models.FloatField(default=10.0)
    # Temperature (°C)  — Safe: 28.0–32.0
    temp_min = models.FloatField(default=28.0)
    temp_max = models.FloatField(default=32.0)
    temp_critical_min = models.FloatField(default=25.0)
    temp_critical_max = models.FloatField(default=35.0)
    # Salinity (ppt)  — Safe: 28.0–33.0
    salinity_min = models.FloatField(default=28.0)
    salinity_max = models.FloatField(default=33.0)
    salinity_critical_min = models.FloatField(default=20.0)
    salinity_critical_max = models.FloatField(default=40.0)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='threshold_updates',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'thresholds'

    def save(self, *args, **kwargs):
        self.pk = 1  # Enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance

    def __str__(self):
        return 'Global Thresholds'
