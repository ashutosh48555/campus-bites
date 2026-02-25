from django.db import models
from orders.models import Order
from shops.models import Shop


class PaymentConfig(models.Model):
    """Shop owner's payment details for accepting online payments."""
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name="payment_config")
    
    # Payment methods
    upi_id = models.CharField(max_length=100, blank=True, help_text="UPI ID (e.g., user@bank)")
    bank_name = models.CharField(max_length=100, blank=True, help_text="Bank name")
    account_number = models.CharField(max_length=50, blank=True, help_text="Account number")
    ifsc_code = models.CharField(max_length=20, blank=True, help_text="IFSC code")
    account_holder_name = models.CharField(max_length=100, blank=True, help_text="Account holder name")
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True, help_text="QR code image for payment")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment Config - {self.shop.name}"


class Payment(models.Model):
    METHOD_CASH = "cash"
    METHOD_ONLINE = "online"

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"

    METHOD_CHOICES = [
        (METHOD_CASH, "Cash"),
        (METHOD_ONLINE, "Online"),
    ]

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.order.id}"
