from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import college_user_required, shop_owner_required
from accounts.models import Notification
from accounts.utils import create_notification
from menu.models import MenuItem
from payments.models import Payment
from shops.models import Shop

from .forms import PickupTimeForm, ExtendPickupTimeForm, FeedbackForm
from .models import Order, OrderItem, Feedback
from .services import round_to_quarter_hour, validate_pickup_time


CART_SESSION_KEY = "cart_items"
CART_SHOP_KEY = "cart_shop_id"


def _get_cart(session):
    return session.get(CART_SESSION_KEY, {})


def _save_cart(session, cart, shop_id):
    session[CART_SESSION_KEY] = cart
    session[CART_SHOP_KEY] = shop_id
    session.modified = True


@login_required
@college_user_required
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    cart = _get_cart(request.session)
    current_shop_id = request.session.get(CART_SHOP_KEY)

    if current_shop_id and str(current_shop_id) != str(item.shop_id):
        cart = {}

    try:
        quantity = int(request.GET.get("qty", 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, min(quantity, 10))  # Ensure qty is between 1 and 10
    
    cart[str(item_id)] = cart.get(str(item_id), 0) + quantity
    _save_cart(request.session, cart, item.shop_id)
    messages.success(request, f"{item.name} added to cart!")
    return redirect("shops:detail", shop_id=item.shop_id)


@login_required
@college_user_required
def view_cart(request):
    cart = _get_cart(request.session)
    items = []
    total = Decimal("0.00")
    for item_id, quantity in cart.items():
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue
        menu_item = get_object_or_404(MenuItem, id=item_id)
        line_total = menu_item.price * quantity
        total += line_total
        items.append({"item": menu_item, "quantity": quantity, "line_total": line_total})

    return render(request, "orders/cart.html", {"items": items, "total": total})


@login_required
@college_user_required
def update_cart_qty(request, item_id):
    cart = _get_cart(request.session)
    action = request.GET.get("action", "increase")
    
    if str(item_id) in cart:
        if action == "increase":
            cart[str(item_id)] = min(cart[str(item_id)] + 1, 10)
        elif action == "decrease":
            cart[str(item_id)] = max(cart[str(item_id)] - 1, 1)
        
        if cart[str(item_id)] == 0:
            del cart[str(item_id)]
    
    shop_id = request.session.get(CART_SHOP_KEY)
    _save_cart(request.session, cart, shop_id)
    return redirect("orders:cart")


@login_required
@college_user_required
def remove_from_cart(request, item_id):
    cart = _get_cart(request.session)
    if str(item_id) in cart:
        del cart[str(item_id)]
    
    shop_id = request.session.get(CART_SHOP_KEY)
    if cart:
        _save_cart(request.session, cart, shop_id)
    else:
        request.session.pop(CART_SESSION_KEY, None)
        request.session.pop(CART_SHOP_KEY, None)
    
    return redirect("orders:cart")



@login_required
@college_user_required
def checkout(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("shops:list")

    shop_id = request.session.get(CART_SHOP_KEY)
    shop = get_object_or_404(Shop, id=shop_id)
    form = PickupTimeForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        pickup_time = round_to_quarter_hour(form.cleaned_data["pickup_time"])
        if timezone.is_naive(pickup_time):
            pickup_time = timezone.make_aware(pickup_time, timezone.get_current_timezone())
        payment_method = form.cleaned_data["payment_method"]

        is_valid, error_message = validate_pickup_time(shop, pickup_time)
        if not is_valid:
            messages.error(request, error_message)
            payment_config = getattr(shop, "payment_config", None)
            return render(request, "orders/checkout.html", {"form": form, "shop": shop, "payment_config": payment_config})

        has_pending = Order.objects.filter(
            user=request.user,
            shop=shop,
            status=Order.STATUS_PENDING,
        ).exists()
        if has_pending:
            messages.error(request, "You already have a pending order for this shop.")
            payment_config = getattr(shop, "payment_config", None)
            return render(request, "orders/checkout.html", {"form": form, "shop": shop, "payment_config": payment_config})

        validated_items = []
        invalid_items = []
        for item_id, quantity in cart.items():
            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                quantity = 1
            if quantity < 1:
                continue
            menu_item = MenuItem.objects.filter(id=item_id, shop=shop, is_available=True).first()
            if not menu_item:
                invalid_items.append(item_id)
                continue
            validated_items.append((menu_item, quantity))

        if invalid_items:
            messages.error(request, "Some items in your cart are no longer available. Please review your cart.")
            return redirect("orders:cart")

        try:
            with transaction.atomic():
                order = Order.objects.create(user=request.user, shop=shop, pickup_time=pickup_time)
                total = Decimal("0.00")
                for menu_item, quantity in validated_items:
                    line_total = menu_item.price * quantity
                    total += line_total
                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=quantity,
                        price=menu_item.price,
                    )
                order.total_price = total
                order.save(update_fields=["total_price"])

                Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    payment_status=(
                        Payment.STATUS_PENDING if payment_method == Payment.METHOD_ONLINE else Payment.STATUS_PAID
                    ),
                )
                
                # Notify shop owner of new order
                create_notification(
                    user=shop.owner,
                    notification_type=Notification.NOTIFICATION_ORDER_PLACED,
                    title=f"New Order #{order.id}",
                    message=f"{request.user.username} placed an order for ₹{order.total_price}. Pickup at {pickup_time.strftime('%I:%M %p')}.",
                    link=f"/shops/owner/dashboard/"
                )
                
        except IntegrityError:
            messages.error(request, "You already have a pending order for this shop.")
            payment_config = getattr(shop, "payment_config", None)
            return render(request, "orders/checkout.html", {"form": form, "shop": shop, "payment_config": payment_config})

        request.session.pop(CART_SESSION_KEY, None)
        request.session.pop(CART_SHOP_KEY, None)
        messages.success(request, "Order placed successfully.")
        return redirect("orders:list")

    payment_config = getattr(shop, "payment_config", None)
    return render(request, "orders/checkout.html", {"form": form, "shop": shop, "payment_config": payment_config})


@login_required
@college_user_required
def order_list(request):
    orders = (
        Order.objects.filter(user=request.user)
        .select_related("shop", "user__profile")
        .prefetch_related("items__menu_item")
        .order_by("-created_at")
    )
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
@college_user_required
def cancel_order(request, order_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Smart cancellation logic
    if order.status == Order.STATUS_PENDING:
        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=["status"])
        
        # Notify shop owner of cancellation
        create_notification(
            user=order.shop.owner,
            notification_type=Notification.NOTIFICATION_ORDER_CANCELLED,
            title=f"Order #{order.id} Cancelled",
            message=f"{request.user.username} cancelled their order for ₹{order.total_price}.",
            link=f"/shops/owner/dashboard/"
        )
        
        messages.success(request, "Order cancelled successfully.")
    elif order.status in [Order.STATUS_PREPARING, Order.STATUS_READY]:
        messages.error(request, "Cannot cancel order - your food is already being prepared or is ready for pickup.")
    elif order.status == Order.STATUS_COLLECTED:
        messages.error(request, "Cannot cancel - order has already been collected.")
    elif order.status == Order.STATUS_CANCELLED:
        messages.info(request, "This order was already cancelled.")
    else:
        messages.error(request, "Unable to cancel this order.")
    
    return redirect("orders:list")


@login_required
@college_user_required
def extend_pickup_time(request, order_id):
    """Allow users to extend pickup time for pending orders only"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Only pending orders can be extended
    if order.status != Order.STATUS_PENDING:
        messages.error(request, "Can only extend pickup time for pending orders.")
        return redirect("orders:list")
    
    if request.method == "POST":
        form = ExtendPickupTimeForm(request.POST)
        if form.is_valid():
            new_pickup_time = round_to_quarter_hour(form.cleaned_data["new_pickup_time"])
            if timezone.is_naive(new_pickup_time):
                new_pickup_time = timezone.make_aware(new_pickup_time, timezone.get_current_timezone())
            
            # Validate new pickup time
            is_valid, error_message = validate_pickup_time(order.shop, new_pickup_time)
            if not is_valid:
                messages.error(request, error_message)
            else:
                order.pickup_time = new_pickup_time
                order.save(update_fields=["pickup_time"])
                
                # Notify shop owner of time extension
                create_notification(
                    user=order.shop.owner,
                    notification_type=Notification.NOTIFICATION_TIME_EXTENDED,
                    title=f"Order #{order.id} Time Extended",
                    message=f"{request.user.username} extended pickup time to {new_pickup_time.strftime('%I:%M %p')}.",
                    link=f"/shops/owner/dashboard/"
                )
                
                messages.success(request, f"Pickup time extended to {new_pickup_time.strftime('%B %d, %Y at %I:%M %p')}.")
                return redirect("orders:list")
    else:
        form = ExtendPickupTimeForm()
    
    return render(request, "orders/extend_pickup_time.html", {"form": form, "order": order})


@login_required
@shop_owner_required
def update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, shop__owner=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            order.save(update_fields=["status"])
            
            # Notify user of status change
            status_messages = {
                Order.STATUS_PREPARING: "Your order is being prepared!",
                Order.STATUS_READY: "Your order is ready for pickup!",
                Order.STATUS_COLLECTED: "Thank you! Order marked as collected.",
            }
            
            notification_types = {
                Order.STATUS_PREPARING: Notification.NOTIFICATION_ORDER_PREPARING,
                Order.STATUS_READY: Notification.NOTIFICATION_ORDER_READY,
                Order.STATUS_COLLECTED: Notification.NOTIFICATION_ORDER_COMPLETED,
            }
            
            if new_status in status_messages and old_status != new_status:
                create_notification(
                    user=order.user,
                    notification_type=notification_types[new_status],
                    title=f"Order #{order.id} Status Update",
                    message=status_messages[new_status],
                    link=f"/orders/"
                )
            
            messages.success(request, "Order status updated.")
    return redirect("shops:owner_dashboard")


@login_required
@college_user_required
def submit_feedback(request, order_id):
    """Submit feedback for a collected order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if feedback already exists
    if hasattr(order, "feedback"):
        messages.info(request, "You have already submitted feedback for this order.")
        return redirect("orders:list")
    
    # Only allow feedback for collected orders
    if order.status != Order.STATUS_COLLECTED:
        messages.error(request, "You can only provide feedback for collected orders.")
        return redirect("orders:list")
    
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.shop = order.shop
            feedback.order = order
            feedback.save()
            
            # Notify shop owner of new feedback
            create_notification(
                user=order.shop.owner,
                notification_type=Notification.NOTIFICATION_FEEDBACK_RECEIVED,
                title=f"New Feedback - {feedback.rating}⭐",
                message=f"{request.user.username} rated your shop {feedback.rating}/5 stars.",
                link=f"/orders/feedbacks/"
            )
            
            messages.success(request, "Thank you for your feedback!")
            return redirect("orders:list")
    else:
        form = FeedbackForm()
    
    return render(request, "orders/feedback_form.html", {"form": form, "order": order})


@login_required
def feedback_list(request):
    """View all feedbacks (for shop owners - their shop, for users - their feedbacks)"""
    if hasattr(request.user, "profile"):
        if request.user.profile.role == "shop_owner":
            # Shop owner sees feedbacks for their shop
            shop = get_object_or_404(Shop, owner=request.user)
            feedbacks = Feedback.objects.filter(shop=shop).select_related("user", "order")
        else:
            # College users see their own feedbacks
            feedbacks = Feedback.objects.filter(user=request.user).select_related("shop", "order")
    else:
        feedbacks = Feedback.objects.none()
    
    return render(request, "orders/feedback_list.html", {"feedbacks": feedbacks})
