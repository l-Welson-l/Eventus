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
    display_name = models.CharField(max_length=50, default="anonymous")

class MagicLinkToken(models.Model):
    token = models.CharField(max_length=256, unique=True)  # we store a signed/jwt or random uuid
    email = models.EmailField()
    anonymous_session = models.ForeignKey(
        AnonymousSession,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # FIXED (business → BusinessProfile)
    business = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name="events"
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)

    qr_code = models.TextField(blank=True)  # base64 QR code
    menu_file = models.FileField(upload_to="event_menus/", null=True, blank=True)
    cover_image = models.ImageField(upload_to="event_covers/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_qr(self):
        from .utils import generate_qr_base64
        url = f"{settings.FRONTEND_BASE_URL}/event/{self.id}"
        self.qr_code = generate_qr_base64(url)
        self.save()
    
    @property
    def has_menu_file(self):
        return bool(self.menu_file)

    def __str__(self):
        return f"{self.name} ({self.business.business_name})"

class EventFeature(models.Model):
    FEATURE_CHOICES = (
        ("menu", "Menu"),
        ("moments", "Moments"),
        ("community", "Community"),
        ("users", "Users"),
        ("leaderboard", "Leaderboard"),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="features")
    key = models.CharField(max_length=50, choices=FEATURE_CHOICES)

    class Meta:
        unique_together = ("event", "key")

    def __str__(self):
        return f"{self.event.name} → {self.key}"

class EventMembership(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    anonymous_session = models.ForeignKey(
        AnonymousSession, null=True, blank=True, on_delete=models.CASCADE
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ("event", "user"),
            ("event", "anonymous_session"),
        )



class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="posts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    anonymous_session = models.ForeignKey('AnonymousSession', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user or 'Anonymous'} in {self.event.name}"