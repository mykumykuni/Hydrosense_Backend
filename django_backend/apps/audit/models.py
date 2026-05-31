import secrets
import time
from django.db import models
from django.conf import settings

AUDIT_MAX_ENTRIES = 200


def _generate_audit_uid():
    ts = int(time.time() * 1000)
    rand = secrets.token_hex(2)  # 4 hex chars
    return f'aud-{ts}-{rand}'


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('clear_all_alerts', 'Clear All Alerts'),
        ('resolve_alert', 'Resolve Alert'),
        ('create_manual_alert', 'Create Manual Alert'),
        ('update_threshold', 'Update Threshold'),
        ('set_history_window', 'Set History Window'),
        ('set_announcement', 'Set Announcement'),
        ('clear_announcement', 'Clear Announcement'),
        ('add_announcement_to_history', 'Add Announcement to History'),
        ('approve_user', 'Approve User'),
        ('deactivate_user', 'Deactivate User'),
    ]

    uid = models.CharField(max_length=32, unique=True, editable=False)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    # Denormalized — preserves history even if the admin account is later deleted
    actor_email = models.EmailField()
    detail = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = _generate_audit_uid()
        super().save(*args, **kwargs)
        # Enforce max entries: remove oldest beyond the cap
        ids_to_keep = (
            AuditLog.objects.order_by('-created_at')
            .values_list('id', flat=True)[:AUDIT_MAX_ENTRIES]
        )
        AuditLog.objects.exclude(id__in=list(ids_to_keep)).delete()

    @property
    def ts(self):
        return int(self.created_at.timestamp() * 1000)

    def __str__(self):
        return f'{self.uid} — {self.actor_email}: {self.action}'
