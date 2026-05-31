from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['email', 'role', 'status', 'approved_at', 'last_login_at', 'is_staff']
    list_filter = ['role', 'status', 'is_staff']
    search_fields = ['email']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('HydroSense', {'fields': ('role', 'status', 'approved_at', 'deactivated_at', 'last_login_at', 'revoked_since')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'position', 'phone']
    search_fields = ['user__email', 'display_name']
