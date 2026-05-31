from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('operator', 'Operator'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Lifecycle timestamps
    approved_at = models.DateTimeField(null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    # All JWTs with iat < revoked_since are invalid (used for forced logout / account suspension)
    revoked_since = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def save(self, *args, **kwargs):
        # Keep username in sync with email for Django internals
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.email} ({self.role})'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=200, blank=True)
    # Base64 data URL of profile photo; stored as text to avoid file-serving complexity
    photo_data_url = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    position = models.CharField(max_length=200, blank=True)
    emergency_contact = models.TextField(blank=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f'{self.user.email} — {self.display_name or self.user.get_full_name()}'
