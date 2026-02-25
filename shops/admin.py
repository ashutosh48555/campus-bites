from django.contrib import admin

from .models import Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "opening_time", "closing_time", "max_orders_per_slot")
    search_fields = ("name", "owner__username", "address")
