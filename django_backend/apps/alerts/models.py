import secrets
import time
from django.db import models
from django.conf import settings

ALERT_MAX_ENTRIES = 300


def _generate_alert_uid():
    ts = int(time.time() * 1000)
    rand = secrets.token_hex(3)  # 6 hex chars
    return f'{ts}-{rand}'


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]

    uid = models.CharField(max_length=32, unique=True, editable=False)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    # Source key: e.g. "do", "ph", "manual-operator", "do-operator-report"
    source = models.CharField(max_length=100)
    resolved = models.BooleanField(default=False)
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='read_alerts',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = _generate_alert_uid()
        super().save(*args, **kwargs)
        # Enforce max entries: remove oldest beyond the cap
        ids_to_keep = (
            Alert.objects.order_by('-created_at')
            .values_list('id', flat=True)[:ALERT_MAX_ENTRIES]
        )
        Alert.objects.exclude(id__in=list(ids_to_keep)).delete()

    @property
    def ts(self):
        return int(self.created_at.timestamp() * 1000)

    def __str__(self):
        return f'[{self.severity.upper()}] {self.title}'
