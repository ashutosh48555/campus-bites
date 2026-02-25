from django.shortcuts import get_object_or_404, redirect
from accounts.decorators import shop_owner_required

from .models import MenuItem


@shop_owner_required
def toggle_availability(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, shop__owner=request.user)
    item.is_available = not item.is_available
    item.save(update_fields=["is_available"])
    return redirect("shops:owner_dashboard")
