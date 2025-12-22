from rest_framework import serializers
import re
from django.contrib.auth import authenticate
from .models import User, BusinessProfile, CustomerProfile, MagicLinkToken, EventFeature, EventMembership, Event
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
        ]