from django.contrib import admin

from .models import Order, OrderItem, Feedback


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "shop", "user", "pickup_time", "status", "total_price", "token_number")
    list_filter = ("status", "shop")
    search_fields = ("user__username", "shop__name")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "menu_item", "quantity", "price")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("shop", "user", "rating", "created_at", "order")
    list_filter = ("rating", "shop", "created_at")
    search_fields = ("user__username", "shop__name", "comment")
    readonly_fields = ("created_at",)
