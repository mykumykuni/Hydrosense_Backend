from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['uid', 'severity', 'title', 'source', 'resolved', 'created_at']
    list_filter = ['severity', 'resolved']
    search_fields = ['title', 'message', 'source', 'uid']
    ordering = ['-created_at']
    readonly_fields = ['uid', 'created_at']
