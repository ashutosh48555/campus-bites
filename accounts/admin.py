from django.contrib import admin

from .models import Profile, Notification


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "college_id", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "college_id")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("user__username", "title", "message")
    readonly_fields = ("created_at",)
