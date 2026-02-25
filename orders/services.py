from datetime import timedelta
from django.utils import timezone

from .models import Order


def round_to_quarter_hour(dt):
    minute = (dt.minute + 7) // 15 * 15
    if minute == 60:
        dt = dt + timedelta(hours=1)
        minute = 0
    return dt.replace(minute=minute, second=0, microsecond=0)


def is_within_shop_hours(shop, pickup_dt):
    return shop.opening_time <= pickup_dt.time() <= shop.closing_time


def is_slot_available(shop, pickup_dt):
    slot_count = Order.objects.filter(
        shop=shop,
        pickup_time=pickup_dt,
    ).exclude(status=Order.STATUS_CANCELLED).count()
    return slot_count < shop.max_orders_per_slot


def validate_pickup_time(shop, pickup_dt):
    now = timezone.localtime(timezone.now())
    if pickup_dt < now + timedelta(minutes=15):
        return False, "Pickup time must be at least 15 minutes from now."
    if not is_within_shop_hours(shop, pickup_dt):
        return False, "Pickup time must be within shop opening hours."
    if not is_slot_available(shop, pickup_dt):
        return False, "Selected time slot is full. Please choose another time."
    return True, ""
