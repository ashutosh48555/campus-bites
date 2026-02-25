from django.conf import settings
from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True, help_text="Shop contact number")
    email = models.EmailField(blank=True, help_text="Shop contact email")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    max_orders_per_slot = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
