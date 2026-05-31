from django.db import models
from django.conf import settings


class Report(models.Model):
    TYPE_CHOICES = [
        ('equipment', 'Equipment'),
        ('water_quality', 'Water Quality'),
        ('general', 'General'),
        ('custom', 'Custom'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    # Auto-set from type for standard types; free text (max 500) for 'custom'
    subject = models.CharField(max_length=500)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reports',
    )
    submitted_by_email = models.EmailField()  # denormalized for history stability
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.priority.upper()}] {self.subject} — {self.status}'


# Subject defaults per type
REPORT_SUBJECT_DEFAULTS = {
    'equipment': 'Equipment Issue',
    'water_quality': 'Water Quality Issue',
    'general': 'General Report',
}


class ReportReply(models.Model):
    """Admin reply thread — only applicable for 'general' and 'custom' report types."""
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='report_replies',
    )
    author_email = models.EmailField()  # denormalized
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'report_replies'
        ordering = ['created_at']

    def __str__(self):
        return f'Reply by {self.author_email} on report #{self.report_id}'
