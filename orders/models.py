import random

from django.conf import settings
from django.db import IntegrityError, models, transaction
from django.db.models import Max, Q

from shops.models import Shop
from menu.models import MenuItem


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PREPARING = "preparing"
    STATUS_READY = "ready"
    STATUS_COLLECTED = "collected"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PREPARING, "Preparing"),
        (STATUS_READY, "Ready"),
        (STATUS_COLLECTED, "Collected"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    pickup_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    token_number = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "token_number"],
                name="unique_token_per_shop",
            ),
            models.UniqueConstraint(
                fields=["user", "shop"],
                condition=Q(status="pending"),
                name="unique_pending_order_per_shop",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.token_number is None:
            for _ in range(10):
                try:
                    with transaction.atomic():
                        # Generate random 4-digit number (1000-9999)
                        self.token_number = random.randint(1000, 9999)
                        super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    self.token_number = None
            raise IntegrityError("Unable to allocate token number for this shop.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.shop.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"


class Feedback(models.Model):
    """Customer feedback for shops and orders"""
    RATING_CHOICES = [
        (1, "1 - Poor"),
        (2, "2 - Fair"),
        (3, "3 - Good"),
        (4, "4 - Very Good"),
        (5, "5 - Excellent"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="feedbacks")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True, related_name="feedback")
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Feedback by {self.user.username} for {self.shop.name} - {self.rating}★"
