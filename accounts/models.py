from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Profile(models.Model):
    ROLE_COLLEGE_USER = "college_user"
    ROLE_SHOP_OWNER = "shop_owner"

    ROLE_CHOICES = [
        (ROLE_COLLEGE_USER, "College User"),
        (ROLE_SHOP_OWNER, "Shop Owner"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    college_id = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.role == self.ROLE_COLLEGE_USER and not self.college_id:
            raise ValidationError({"college_id": "College ID is required for college users."})

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Notification(models.Model):
    NOTIFICATION_ORDER_PLACED = "order_placed"
    NOTIFICATION_ORDER_PREPARING = "order_preparing"
    NOTIFICATION_ORDER_READY = "order_ready"
    NOTIFICATION_ORDER_COMPLETED = "order_completed"
    NOTIFICATION_ORDER_CANCELLED = "order_cancelled"
    NOTIFICATION_FEEDBACK_RECEIVED = "feedback_received"
    NOTIFICATION_TIME_EXTENDED = "time_extended"

    NOTIFICATION_TYPES = [
        (NOTIFICATION_ORDER_PLACED, "New Order Placed"),
        (NOTIFICATION_ORDER_PREPARING, "Order Being Prepared"),
        (NOTIFICATION_ORDER_READY, "Order Ready for Pickup"),
        (NOTIFICATION_ORDER_COMPLETED, "Order Completed"),
        (NOTIFICATION_ORDER_CANCELLED, "Order Cancelled"),
        (NOTIFICATION_FEEDBACK_RECEIVED, "Feedback Received"),
        (NOTIFICATION_TIME_EXTENDED, "Pickup Time Extended"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
