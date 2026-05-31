from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['uid', 'action', 'actor_email', 'detail', 'created_at']
    list_filter = ['action']
    search_fields = ['uid', 'actor_email', 'detail']
    ordering = ['-created_at']
    readonly_fields = ['uid', 'action', 'actor_email', 'detail', 'created_at']
