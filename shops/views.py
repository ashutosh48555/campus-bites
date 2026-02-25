from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum, Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import shop_owner_required
from menu.models import MenuItem, Category
from menu.forms import MenuItemForm, CategoryForm
from orders.models import Order, Feedback

from .models import Shop
from .forms import ShopForm


def shop_list(request):
    query = request.GET.get('q', '').strip()
    shops = Shop.objects.all()
    
    if query:
        shops = shops.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(address__icontains=query)
        )
    
    shops = shops.order_by("name")
    return render(request, "shops/shop_list.html", {"shops": shops, "query": query})


def shop_detail(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    items = MenuItem.objects.filter(shop=shop, is_available=True).select_related("category")
    
    # Get cart items count
    cart = request.session.get("cart_items", {})
    cart_items_count = 0
    for quantity in cart.values():
        try:
            cart_items_count += int(quantity)
        except (TypeError, ValueError):
            continue
    
    return render(request, "shops/shop_detail.html", {"shop": shop, "items": items, "cart_items_count": cart_items_count})


def search_menu(request):
    """Search for menu items across all shops"""
    query = request.GET.get('q', '').strip()
    items = []
    
    if query:
        items = MenuItem.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_available=True
        ).select_related("shop", "category").order_by("shop__name", "name")
    
    return render(request, "shops/search_results.html", {"items": items, "query": query})


@login_required
@shop_owner_required
def owner_dashboard(request):
    shop = get_object_or_404(Shop, owner=request.user)
    today_orders = (
        Order.objects.filter(shop=shop, pickup_time__date=date.today())
        .select_related("user", "user__profile")
        .prefetch_related("items__menu_item")
        .order_by("pickup_time")
    )
    return render(request, "shops/owner_dashboard.html", {"shop": shop, "orders": today_orders})


# === MENU MANAGEMENT VIEWS ===

@login_required
@shop_owner_required
def manage_menu(request):
    """List all menu items for the shop owner's shop"""
    shop = get_object_or_404(Shop, owner=request.user)
    items = MenuItem.objects.filter(shop=shop).select_related("category").order_by("category__name", "name")
    categories = Category.objects.filter(shop=shop).order_by("name")
    return render(request, "shops/manage_menu.html", {"shop": shop, "items": items, "categories": categories})


@login_required
@shop_owner_required
def add_menu_item(request):
    """Add a new menu item"""
    shop = get_object_or_404(Shop, owner=request.user)
    
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, shop=shop)
        if form.is_valid():
            item = form.save(commit=False)
            item.shop = shop
            item.save()
            messages.success(request, f"Menu item '{item.name}' added successfully!")
            return redirect("shops:manage_menu")
    else:
        form = MenuItemForm(shop=shop)
    
    return render(request, "shops/menu_item_form.html", {"form": form, "shop": shop, "action": "Add"})


@login_required
@shop_owner_required
def edit_menu_item(request, item_id):
    """Edit an existing menu item"""
    shop = get_object_or_404(Shop, owner=request.user)
    item = get_object_or_404(MenuItem, id=item_id, shop=shop)
    
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, instance=item, shop=shop)
        if form.is_valid():
            form.save()
            messages.success(request, f"Menu item '{item.name}' updated successfully!")
            return redirect("shops:manage_menu")
    else:
        form = MenuItemForm(instance=item, shop=shop)
    
    return render(request, "shops/menu_item_form.html", {"form": form, "shop": shop, "item": item, "action": "Edit"})


@login_required
@shop_owner_required
def delete_menu_item(request, item_id):
    """Delete a menu item"""
    shop = get_object_or_404(Shop, owner=request.user)
    item = get_object_or_404(MenuItem, id=item_id, shop=shop)
    
    if request.method == "POST":
        item_name = item.name
        item.delete()
        messages.success(request, f"Menu item '{item_name}' deleted successfully!")
        return redirect("shops:manage_menu")
    
    return render(request, "shops/confirm_delete.html", {"shop": shop, "item": item, "type": "menu item"})


@login_required
@shop_owner_required
def toggle_item_availability(request, item_id):
    """Toggle menu item availability (mark out of stock)"""
    shop = get_object_or_404(Shop, owner=request.user)
    item = get_object_or_404(MenuItem, id=item_id, shop=shop)
    
    item.is_available = not item.is_available
    item.save()
    
    status = "available" if item.is_available else "out of stock"
    messages.success(request, f"'{item.name}' is now marked as {status}!")
    return redirect("shops:manage_menu")


# === CATEGORY MANAGEMENT VIEWS ===

@login_required
@shop_owner_required
def add_category(request):
    """Add a new category"""
    shop = get_object_or_404(Shop, owner=request.user)
    
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.shop = shop
            category.save()
            messages.success(request, f"Category '{category.name}' added successfully!")
            return redirect("shops:manage_menu")
    else:
        form = CategoryForm()
    
    return render(request, "shops/category_form.html", {"form": form, "shop": shop, "action": "Add"})


@login_required
@shop_owner_required
def edit_category(request, category_id):
    """Edit an existing category"""
    shop = get_object_or_404(Shop, owner=request.user)
    category = get_object_or_404(Category, id=category_id, shop=shop)
    
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated successfully!")
            return redirect("shops:manage_menu")
    else:
        form = CategoryForm(instance=category)
    
    return render(request, "shops/category_form.html", {"form": form, "shop": shop, "category": category, "action": "Edit"})


@login_required
@shop_owner_required
def delete_category(request, category_id):
    """Delete a category"""
    shop = get_object_or_404(Shop, owner=request.user)
    category = get_object_or_404(Category, id=category_id, shop=shop)
    
    if request.method == "POST":
        category_name = category.name
        category.delete()
        messages.success(request, f"Category '{category_name}' deleted successfully!")
        return redirect("shops:manage_menu")
    
    return render(request, "shops/confirm_delete.html", {"shop": shop, "item": category, "type": "category"})


# === SHOP SETTINGS ===

@login_required
@shop_owner_required
def edit_shop_settings(request):
    """Edit shop details and settings"""
    shop = get_object_or_404(Shop, owner=request.user)
    
    if request.method == "POST":
        form = ShopForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, "Shop settings updated successfully!")
            return redirect("shops:owner_dashboard")
    else:
        form = ShopForm(instance=shop)
    
    return render(request, "shops/shop_settings.html", {"form": form, "shop": shop})


@login_required
@shop_owner_required
def analytics_dashboard(request):
    """Sales analytics and performance dashboard for shop owners with ML insights"""
    from .analytics_service import ShopAnalyticsService
    from datetime import datetime
    
    shop = get_object_or_404(Shop, owner=request.user)
    analytics = ShopAnalyticsService(shop)
    
    # Date range filter - support both period and custom dates
    period = request.GET.get('period', '30')  # Default 30 days
    report_type = request.GET.get('report', 'daily')  # daily, weekly, monthly, hourly
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Determine date range
    end_date = timezone.now()
    
    if start_date_str and end_date_str:
        # Use custom date range
        try:
            start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
            end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d')).replace(hour=23, minute=59, second=59)
            days = (end_date - start_date).days + 1
        except ValueError:
            # Fall back to period if date parsing fails
            try:
                days = int(period)
            except ValueError:
                days = 30
            start_date = timezone.now() - timedelta(days=days)
    else:
        # Use period
        try:
            days = int(period)
        except ValueError:
            days = 30
        start_date = timezone.now() - timedelta(days=days)
    
    # Calculate previous period for growth comparison
    period_length = (end_date - start_date).days + 1
    previous_start = start_date - timedelta(days=period_length)
    previous_end = start_date
    
    # Current period orders
    orders_in_period = Order.objects.filter(shop=shop, created_at__gte=start_date, created_at__lte=end_date)
    
    # Previous period orders
    previous_orders = Order.objects.filter(shop=shop, created_at__gte=previous_start, created_at__lt=previous_end)
    
    period_stats = {
        'total_orders': orders_in_period.count(),
        'pending': orders_in_period.filter(status=Order.STATUS_PENDING).count(),
        'preparing': orders_in_period.filter(status=Order.STATUS_PREPARING).count(),
        'ready': orders_in_period.filter(status=Order.STATUS_READY).count(),
        'collected': orders_in_period.filter(status=Order.STATUS_COLLECTED).count(),
        'cancelled': orders_in_period.filter(status=Order.STATUS_CANCELLED).count(),
    }
    
    # Revenue statistics (current period)
    completed_orders = orders_in_period.filter(status=Order.STATUS_COLLECTED)
    total_revenue = completed_orders.aggregate(total=Sum('total_price'))['total'] or 0
    avg_order_value = completed_orders.aggregate(avg=Avg('total_price'))['avg'] or 0
    
    # Previous period revenue for growth calculation
    previous_completed = previous_orders.filter(status=Order.STATUS_COLLECTED)
    previous_revenue = previous_completed.aggregate(total=Sum('total_price'))['total'] or 0
    
    # Calculate revenue growth percentage
    if previous_revenue > 0:
        revenue_growth = ((total_revenue - previous_revenue) / previous_revenue) * 100
    else:
        revenue_growth = 100 if total_revenue > 0 else 0
    
    # All-time revenue
    all_time_revenue = Order.objects.filter(
        shop=shop, 
        status=Order.STATUS_COLLECTED
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Feedback statistics
    feedbacks = Feedback.objects.filter(shop=shop, created_at__gte=start_date, created_at__lte=end_date)
    avg_rating = feedbacks.aggregate(avg=Avg('rating'))['avg'] or 0
    total_feedbacks = feedbacks.count()
    
    # Rating distribution
    rating_distribution = {
        '5': feedbacks.filter(rating=5).count(),
        '4': feedbacks.filter(rating=4).count(),
        '3': feedbacks.filter(rating=3).count(),
        '2': feedbacks.filter(rating=2).count(),
        '1': feedbacks.filter(rating=1).count(),
    }
    
    # === Advanced Analytics Features (using actual days) ===
    
    # Most and least ordered items
    most_ordered = analytics.get_most_ordered_items(days, limit=10)
    least_sold = analytics.get_least_sold_items(days, limit=10)
    
    # Payment method analysis
    payment_analysis = analytics.get_payment_method_analysis(days)
    
    # Peak hours analysis
    peak_hours = analytics.get_peak_hours_analysis(days)
    
    # Get appropriate report based on type
    if report_type == 'hourly':
        time_report = analytics.get_hourly_report(24)
    elif report_type == 'weekly':
        time_report = analytics.get_weekly_report(4)
    elif report_type == 'monthly':
        time_report = analytics.get_monthly_report(12)
    else:  # daily
        time_report = analytics.get_daily_report(min(days, 90))
    
    # ML-based insights and recommendations
    ml_insights = analytics.get_ml_insights(days)
    
    context = {
        'shop': shop,
        'period': days,
        'report_type': report_type,
        'start_date': start_date,
        'end_date': end_date,
        'total_orders': orders_in_period.count(),
        'period_stats': period_stats,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'all_time_revenue': all_time_revenue,
        'avg_rating': avg_rating,
        'total_feedbacks': total_feedbacks,
        'rating_distribution': rating_distribution,
        'revenue_growth': revenue_growth,
        
        # Advanced analytics
        'most_ordered': most_ordered,
        'least_sold': least_sold,
        'payment_analysis': payment_analysis,
        'peak_hours': peak_hours,
        'time_report': time_report,
        'ml_insights': ml_insights,
    }
    
    return render(request, "shops/analytics.html", context)

