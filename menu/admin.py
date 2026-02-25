from django.contrib import admin

from .models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "shop")
    search_fields = ("name", "shop__name")


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "shop", "price", "is_available")
    list_filter = ("shop", "is_available")
    search_fields = ("name", "shop__name")
