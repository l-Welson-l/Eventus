from django.contrib import admin
from .models import User, BusinessProfile, CustomerProfile


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ("user_email", "business_name", "address", "created_at", "email_verified")
    search_fields = ("business_name", "user__email")
    list_filter = ("email_verified",)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user_email", "joined_at")
    search_fields = ("user__email",)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"

