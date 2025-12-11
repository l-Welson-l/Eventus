from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import secrets
from datetime import timedelta

User = get_user_model()

# Named functions for defaults (lambda removed)
def make_random(length=24):
    return secrets.token_urlsafe(length)[:length]

def generate_admin_token():
    return secrets.token_urlsafe(48)

def generate_session_token():
    return secrets.token_urlsafe(48)


class Event(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    name = models.CharField(max_length=255)
    venue_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    view_code = models.CharField(max_length=16, unique=True, default=make_random)
    admin_token = models.CharField(max_length=48, unique=True, default=generate_admin_token)

    auto_approve = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.venue_name or self.name} ({self.id})"
    

class PostingSession(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="sessions")
    token = models.CharField(max_length=64, unique=True, default=generate_session_token)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    device_id = models.CharField(max_length=128, blank=True, null=True)

    @classmethod
    def create_for_event(cls, event, hours_valid=8, device_id=None):
        return cls.objects.create(
            event=event,
            token=generate_session_token(),
            valid_until=timezone.now() + timedelta(hours=hours_valid),
            device_id=device_id,
        )

    def is_valid(self):
        return timezone.now() <= self.valid_until


class Post(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="posts")
    session = models.ForeignKey(PostingSession, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to="posts/%Y/%m/%d/")
    caption = models.TextField(blank=True)
    approved = models.BooleanField(default=True)
    likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
