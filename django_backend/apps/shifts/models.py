import secrets
import time
from django.db import models
from django.conf import settings

SHIFT_LOG_MAX_ENTRIES = 100


def _generate_shift_uid():
    ts = int(time.time() * 1000)
    rand = secrets.token_hex(3)  # 6 hex chars
    return f'sl-{ts}-{rand}'


class ShiftLog(models.Model):
    """Operator shift notes — max 100 entries, oldest pruned automatically."""

    uid = models.CharField(max_length=32, unique=True, editable=False)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='shift_logs',
    )
    # Denormalized for history stability
    operator_email = models.EmailField()
    operator_name = models.CharField(max_length=200)
    note = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shift_logs'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = _generate_shift_uid()
        super().save(*args, **kwargs)
        # Enforce max entries: remove oldest beyond the cap
        ids_to_keep = (
            ShiftLog.objects.order_by('-created_at')
            .values_list('id', flat=True)[:SHIFT_LOG_MAX_ENTRIES]
        )
        ShiftLog.objects.exclude(id__in=list(ids_to_keep)).delete()

    @property
    def ts(self):
        return int(self.created_at.timestamp() * 1000)

    def __str__(self):
        return f'{self.uid} — {self.operator_email}'
