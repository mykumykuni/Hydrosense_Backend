from django.contrib import admin
from .models import Report, ReportReply


class ReportReplyInline(admin.TabularInline):
    model = ReportReply
    extra = 0
    readonly_fields = ['author', 'author_email', 'created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['subject', 'type', 'priority', 'status', 'submitted_by_email', 'created_at']
    list_filter = ['type', 'priority', 'status']
    search_fields = ['subject', 'message', 'submitted_by_email']
    inlines = [ReportReplyInline]
    readonly_fields = ['submitted_by', 'submitted_by_email', 'created_at', 'updated_at']


@admin.register(ReportReply)
class ReportReplyAdmin(admin.ModelAdmin):
    list_display = ['report', 'author_email', 'created_at']
    readonly_fields = ['author', 'author_email', 'created_at']
