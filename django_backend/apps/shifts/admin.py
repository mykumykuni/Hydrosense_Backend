from django.contrib import admin
from .models import ShiftLog


@admin.register(ShiftLog)
class ShiftLogAdmin(admin.ModelAdmin):
    list_display = ['uid', 'operator_email', 'operator_name', 'created_at']
    search_fields = ['uid', 'operator_email', 'operator_name', 'note']
    ordering = ['-created_at']
    readonly_fields = ['uid', 'operator', 'operator_email', 'operator_name', 'created_at']
