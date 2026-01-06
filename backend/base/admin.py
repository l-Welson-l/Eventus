from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import (
    User,
    BusinessProfile,
    CustomerProfile,
    Event,
    Post,
    AnonymousSession,
    MagicLinkToken,
    EventFeature, 
    Moment,
    MomentMedia,
    MomentLike,
    Menu,
    MenuCategory,
    MenuItem,

)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ("email", "username", "user_type", "is_staff", "is_active")
    list_filter = ("user_type", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("username", "first_name", "last_name", "user_type")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "user_type", "password1", "password2"),
        }),
    )

    search_fields = ("email", "username")
    ordering = ("email",)


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "user", "email_verified", "created_at")
    search_fields = ("business_name", "user__email")


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "joined_at")
    search_fields = ("user__email",)

class EventFeatureInline(admin.TabularInline):
    model = EventFeature
    extra = 1



@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "business",
        "start_time",
        "end_time",
        "created_at",
        "qr_preview",
    )

    search_fields = ("name", "business__business_name")
    list_filter = ("start_time",)

    readonly_fields = ("qr_preview", "created_at", "updated_at")

    inlines = [EventFeatureInline]  # 👈 ADD THIS

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not obj.qr_code:
            obj.generate_qr()

    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="150" height="150" />',
                obj.qr_code
            )
        return "No QR generated"

    qr_preview.short_description = "QR Code"



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "created_at")
    list_filter = ("created_at",)


@admin.register(AnonymousSession)
class AnonymousSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "email", "created_at", "last_active")


@admin.register(MagicLinkToken)
class MagicLinkTokenAdmin(admin.ModelAdmin):
    list_display = ("email", "used", "expires_at", "created_at")
    list_filter = ("used",)

class MomentMediaInline(admin.TabularInline):
    model = MomentMedia
    extra = 0


@admin.register(Moment)
class MomentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event",
        "user",
        "anonymous_session",
        "likes_count",
        "created_at",
    )

    list_filter = ("event", "created_at")
    search_fields = ("caption",)

    inlines = [MomentMediaInline]

    readonly_fields = ("likes_count", "created_at")


@admin.register(MomentMedia)
class MomentMediaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "moment",
        "media_type",
        "order",
        "created_at",
    )

    list_filter = ("media_type",)


@admin.register(MomentLike)
class MomentLikeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "moment",
        "user",
        "anonymous_session",
        "created_at",
    )

    list_filter = ("created_at",)


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ("name", "price", "description", "image", "order")

class MenuCategoryInline(admin.StackedInline):
    model = MenuCategory
    extra = 1
    fields = ("name", "order")

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("event", "title", "created_at")
    search_fields = ("event__name", "title")
    inlines = [MenuCategoryInline]


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "menu", "order")
    ordering = ("menu", "order")
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "order")
    list_editable = ("price", "order")
    search_fields = ("name",)
