from rest_framework import serializers
from .models import Event, PostingSession, Post

class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "venue_name", "description", "view_code", "admin_token", "auto_approve"]

class PostingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostingSession
        fields = ["token", "valid_until", "device_id"]

class PostSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "image_url", "caption", "likes", "approved", "created_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not request:
            return obj.image.url
        return request.build_absolute_uri(obj.image.url)
