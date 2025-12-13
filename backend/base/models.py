from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import secrets
from datetime import timedelta


# Named functions for defaults (lambda removed)
def make_random(length=24):
    return secrets.token_urlsafe(length)[:length]

def generate_admin_token():
    return secrets.token_urlsafe(48)

def generate_session_token():
    return secrets.token_urlsafe(48)

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('business', 'Business'),
        ('customer', 'Customer'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    username = models.CharField(unique=True, max_length=50)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="business_profile")
    business_name = models.CharField(max_length=255)
    address = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)
    cover_photo = models.ImageField(upload_to='cover_photos/', null=True, blank=True)

    def __str__(self):
        return self.business_name


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    cover_photo = models.ImageField(upload_to='cover_photos/', null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)


class AnonymousSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    email = models.EmailField(null=True, blank=True)

class MagicLinkToken(models.Model):
    token = models.CharField(max_length=256, unique=True)  # we store a signed/jwt or random uuid
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

