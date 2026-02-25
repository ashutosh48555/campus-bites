from django.contrib import admin

from .models import Payment, PaymentConfig


@admin.register(PaymentConfig)
class PaymentConfigAdmin(admin.ModelAdmin):
    list_display = ("shop", "upi_id", "bank_name", "updated_at")
    search_fields = ("shop__name", "upi_id")
    fieldsets = (
        ("Shop", {"fields": ("shop",)}),
        ("UPI Payment", {"fields": ("upi_id",)}),
        ("Bank Transfer", {"fields": ("bank_name", "account_holder_name", "account_number", "ifsc_code")}),
        ("QR Code", {"fields": ("qr_code",)}),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "payment_method", "payment_status", "created_at")
    list_filter = ("payment_method", "payment_status")
