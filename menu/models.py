from django.db import models
from shops.models import Shop


class Category(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.shop.name})"


class MenuItem(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    preparation_time_minutes = models.PositiveIntegerField(default=10)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.shop.name})"
