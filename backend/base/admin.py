from django.contrib import admin
from .models import Event, PostingSession, Post

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "venue_name", "owner", "view_code", "admin_token", "auto_approve", "created_at")
    search_fields = ("name", "venue_name", "owner__username", "view_code")
    readonly_fields = ("view_code", "admin_token", "created_at")


@admin.register(PostingSession)
class PostingSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "token", "device_id", "created_at", "valid_until")
    search_fields = ("event__name", "token", "device_id")
    readonly_fields = ("token", "created_at")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "session", "caption", "approved", "likes", "created_at")
    list_filter = ("approved", "event")
    search_fields = ("caption", "event__name", "session__token")
