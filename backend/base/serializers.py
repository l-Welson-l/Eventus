from rest_framework import serializers
import re
from django.contrib.auth import authenticate
from .models import User, BusinessProfile, CustomerProfile, MagicLinkToken, EventFeature, EventMembership, Event, Comment, Post
from .utils import validate_email


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "user_type"]
        read_only_fields = ["id", "email"]

class BusinessProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = BusinessProfile
        fields = ["user", "business_name", "address", "created_at", "email_verified", "cover_photo"]
        read_only_fields = ["created_at", "email_verified"]


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ["user", "cover_photo", "joined_at"]
        read_only_fields = ["joined_at"]

class EventFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventFeature
        fields = ["key"]



class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    address = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )
    class Meta:
        model = User
        fields = ["email", "username", "user_type", "password1", "password2", "address",]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("Password do not match!")
        password = attrs.get("password1", "")
        if len(password) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters!"
            )
            # ✅ business-specific validation
        if attrs.get("user_type") == "business":
            if not attrs.get("address"):
                raise serializers.ValidationError({
                    "address": "Address is required for business accounts."
                })

        return attrs

    def validate_email(self, value):
        if not validate_email(value):
            raise serializers.ValidationError("Invalid Email")
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        # ✅ REMOVE fields not belonging to User
        address = validated_data.pop("address", "")
        password = validated_data.pop("password1")
        validated_data.pop("password2")

        # ✅ Create user ONLY with User fields
        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        # ✅ Create correct profile
        if user.user_type == "business":
            BusinessProfile.objects.create(
                user=user,
                business_name=user.username,
                address=address
            )
        else:
            CustomerProfile.objects.create(user=user)

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get("email")
        password = data.get("password")

        user = authenticate(username=identifier, password=password)
        if not user:
            raise serializers.ValidationError("Incorrect credentials.")
        if not user.is_active:
            raise serializers.ValidationError("Account deactivated.")
        return {"user": user}
    

class EventSerializer(serializers.ModelSerializer):
    features = EventFeatureSerializer(many=True)
    menu_file_url = serializers.SerializerMethodField() 
    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "description",
            "start_time",
            "end_time",
            "qr_code",
            "features",

            "menu_file",   # ✅ added
            "cover_image",
            "menu_file_url", # ✅ optional
            "features"
        ]

    def get_menu_file_url(self, obj):
        if obj.menu_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.menu_file.url)
            return obj.menu_file.url
        return None


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["post", "user", "anonymous_session"]

    def get_author_name(self, obj):
        if obj.user:
            return obj.user.username.lower()
        if obj.anonymous_session:
            return f"anonymous_{str(obj.anonymous_session.session_id)[:4]}"
        return "Anonymous"


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    image = serializers.ImageField(required=False)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ["event", "user", "anonymous_session"]

    def get_author_name(self, obj):
        if obj.user:
            return obj.user.username.lower()
        if obj.anonymous_session:
            return f"anonymous_{str(obj.anonymous_session.session_id)[:4]}"
        return "Anonymous"
    
