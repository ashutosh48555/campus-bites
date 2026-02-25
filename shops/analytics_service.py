"""
Advanced Analytics Service for Shop Performance Analysis
Includes ML and Data Science features for comprehensive business insights
"""

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
import statistics


class ShopAnalyticsService:
    """
    Comprehensive analytics service for shop owners
    Provides ML-based insights and data-driven recommendations
    """
    
    def __init__(self, shop):
        self.shop = shop
    
    def get_time_range(self, period_type='daily', days=None):
        """Get time range based on period type"""
        now = timezone.now()
        
        if period_type == 'hourly':
            start_date = now - timedelta(days=1)  # Last 24 hours
        elif period_type == 'daily':
            start_date = now - timedelta(days=days or 30)
        elif period_type == 'weekly':
            start_date = now - timedelta(weeks=4)  # Last 4 weeks
        elif period_type == 'monthly':
            start_date = now - timedelta(days=365)  # Last 12 months
        else:
            start_date = now - timedelta(days=7)
        
        return start_date, now
    
    def get_most_ordered_items(self, period_days=30, limit=10):
        """
        Analyze most ordered items with quantity, revenue, and frequency metrics
        """
        from orders.models import OrderItem, Order
        
        start_date = timezone.now() - timedelta(days=period_days)
        
        items = (
            OrderItem.objects
            .filter(
                order__shop=self.shop,
                order__created_at__gte=start_date,
                order__status=Order.STATUS_COLLECTED
            )
            .values('menu_item__id', 'menu_item__name', 'menu_item__category__name')
            .annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum(F('quantity') * F('price')),
                order_count=Count('order', distinct=True),
                avg_quantity_per_order=Avg('quantity')
            )
            .order_by('-total_quantity')[:limit]
        )
        
        return list(items)
    
    def get_least_sold_items(self, period_days=30, limit=10):
        """
        Identify least sold items that might need promotion or removal
        """
        from orders.models import OrderItem, Order
        from menu.models import MenuItem
        
        start_date = timezone.now() - timedelta(days=period_days)
        
        # Get all available menu items
        all_items = MenuItem.objects.filter(shop=self.shop, is_available=True)
        
        # Get items with their sales
        items_with_sales = (
            OrderItem.objects
            .filter(
                order__shop=self.shop,
                order__created_at__gte=start_date,
                order__status=Order.STATUS_COLLECTED
            )
            .values('menu_item__id', 'menu_item__name', 'menu_item__category__name')
            .annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum(F('quantity') * F('price')),
                order_count=Count('order', distinct=True)
            )
            .order_by('total_quantity')[:limit]
        )
        
        # Also find items with zero sales
        items_with_sales_ids = OrderItem.objects.filter(
            order__shop=self.shop,
            order__created_at__gte=start_date
        ).values_list('menu_item__id', flat=True).distinct()
        
        zero_sales_items = all_items.exclude(id__in=items_with_sales_ids).values(
            'id', 'name', 'category__name', 'price'
        )[:limit]
        
        # Combine and format
        least_sold = []
        
        for item in zero_sales_items:
            least_sold.append({
                'menu_item__id': item['id'],
                'menu_item__name': item['name'],
                'menu_item__category__name': item['category__name'],
                'total_quantity': 0,
                'total_revenue': Decimal('0.00'),
                'order_count': 0,
                'status': 'No sales'
            })
        
        for item in items_with_sales:
            if len(least_sold) < limit:
                item['status'] = 'Low sales'
                least_sold.append(item)
        
        return least_sold[:limit]
    
    def get_payment_method_analysis(self, period_days=30):
        """
        Analyze payment method preferences with detailed breakdown
        """
        from payments.models import Payment
        from orders.models import Order
        
        start_date = timezone.now() - timedelta(days=period_days)
        
        payment_stats = (
            Payment.objects
            .filter(
                order__shop=self.shop,
                order__created_at__gte=start_date,
                payment_status=Payment.STATUS_PAID
            )
            .values('payment_method')
            .annotate(
                count=Count('id'),
                total_amount=Sum('order__total_price'),
                avg_amount=Avg('order__total_price')
            )
            .order_by('-count')
        )
        
        total_payments = sum(stat['count'] for stat in payment_stats)
        
        # Calculate percentages and format data
        payment_data = []
        for stat in payment_stats:
            percentage = (stat['count'] / total_payments * 100) if total_payments > 0 else 0
            payment_data.append({
                'method': 'Cash on Pickup' if stat['payment_method'] == 'cash' else 'Online Payment',
                'method_code': stat['payment_method'],
                'count': stat['count'],
                'percentage': round(percentage, 2),
                'total_amount': stat['total_amount'] or Decimal('0.00'),
                'avg_amount': stat['avg_amount'] or Decimal('0.00')
            })
        
        return {
            'methods': payment_data,
            'total_transactions': total_payments,
            'most_used': payment_data[0] if payment_data else None
        }
    
    def get_peak_hours_analysis(self, period_days=30):
        """
        Identify peak hours for orders using time-series analysis
        """
        from orders.models import Order
        
        start_date = timezone.now() - timedelta(days=period_days)
        
        # Get all orders in the period
        orders = Order.objects.filter(
            shop=self.shop,
            created_at__gte=start_date
        ).values_list('created_at', flat=True)
        
        # Analyze by hour of day
        hourly_distribution = defaultdict(int)
        for order_time in orders:
            hour = order_time.hour
            hourly_distribution[hour] += 1
        
        # Format hourly data
        hourly_data = []
        for hour in range(24):
            count = hourly_distribution.get(hour, 0)
            hourly_data.append({
                'hour': hour,
                'hour_label': f"{hour:02d}:00",
                'count': count,
                'period': self._get_time_period_label(hour)
            })
        
        # Find peak hours (top 3)
        sorted_hours = sorted(hourly_data, key=lambda x: x['count'], reverse=True)
        peak_hours = sorted_hours[:3]
        
        # Find slow hours (bottom 3 with activity)
        slow_hours = [h for h in sorted_hours if h['count'] > 0][-3:] if sorted_hours else []
        
        return {
            'hourly_distribution': hourly_data,
            'peak_hours': peak_hours,
            'slow_hours': slow_hours,
            'busiest_hour': peak_hours[0] if peak_hours else None
        }
    
    def get_daily_report(self, days=30):
        """
        Daily performance report with trends
        """
        from orders.models import Order
        
        start_date = timezone.now() - timedelta(days=days)
        end_date = timezone.now()
        
        daily_data = []
        current_date = start_date.date()
        
        while current_date <= end_date.date():
            orders = Order.objects.filter(
                shop=self.shop,
                created_at__date=current_date
            )
            
            completed = orders.filter(status=Order.STATUS_COLLECTED)
            revenue = completed.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
            
            daily_data.append({
                'date': current_date,
                'date_label': current_date.strftime('%Y-%m-%d'),
                'day_name': current_date.strftime('%A'),
                'total_orders': orders.count(),
                'completed_orders': completed.count(),
                'revenue': revenue,
                'avg_order_value': revenue / completed.count() if completed.count() > 0 else Decimal('0.00')
            })
            
            current_date += timedelta(days=1)
        
        # Calculate trend
        if len(daily_data) >= 7:
            recent_avg = statistics.mean([d['total_orders'] for d in daily_data[-7:]])
            previous_avg = statistics.mean([d['total_orders'] for d in daily_data[-14:-7]]) if len(daily_data) >= 14 else recent_avg
            trend = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
        else:
            trend = 0
        
        return {
            'daily_data': daily_data,
            'trend_percentage': round(trend, 2),
            'trend_direction': 'up' if trend > 0 else 'down' if trend < 0 else 'stable'
        }
    
    def get_weekly_report(self, weeks=4):
        """
        Weekly aggregated performance report
        """
        from orders.models import Order
        
        weekly_data = []
        now = timezone.now()
        
        for i in range(weeks):
            week_end = now - timedelta(weeks=i)
            week_start = week_end - timedelta(days=7)
            
            orders = Order.objects.filter(
                shop=self.shop,
                created_at__gte=week_start,
                created_at__lt=week_end
            )
            
            completed = orders.filter(status=Order.STATUS_COLLECTED)
            revenue = completed.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
            
            weekly_data.append({
                'week_start': week_start.date(),
                'week_end': week_end.date(),
                'week_label': f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}",
                'total_orders': orders.count(),
                'completed_orders': completed.count(),
                'revenue': revenue,
                'avg_daily_orders': orders.count() / 7
            })
        
        weekly_data.reverse()
        return {'weekly_data': weekly_data}
    
    def get_monthly_report(self, months=12):
        """
        Monthly performance report with year-over-year comparison
        """
        from orders.models import Order
        
        monthly_data = []
        now = timezone.now()
        
        for i in range(months):
            # Calculate month start and end
            if i == 0:
                month_end = now
                month_start = now.replace(day=1)
            else:
                month_end = (now.replace(day=1) - timedelta(days=1))
                for _ in range(i - 1):
                    month_end = (month_end.replace(day=1) - timedelta(days=1))
                month_start = month_end.replace(day=1)
            
            orders = Order.objects.filter(
                shop=self.shop,
                created_at__gte=month_start,
                created_at__lt=month_end + timedelta(days=1)
            )
            
            completed = orders.filter(status=Order.STATUS_COLLECTED)
            revenue = completed.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
            
            monthly_data.append({
                'month': month_start.strftime('%B %Y'),
                'month_short': month_start.strftime('%b %Y'),
                'year': month_start.year,
                'month_num': month_start.month,
                'total_orders': orders.count(),
                'completed_orders': completed.count(),
                'revenue': revenue,
                'avg_order_value': revenue / completed.count() if completed.count() > 0 else Decimal('0.00')
            })
        
        monthly_data.reverse()
        return {'monthly_data': monthly_data}
    
    def get_hourly_report(self, hours=24):
        """
        Hourly report for the last 24 hours
        """
        from orders.models import Order
        
        hourly_data = []
        now = timezone.now()
        
        for i in range(hours):
            hour_end = now - timedelta(hours=i)
            hour_start = hour_end - timedelta(hours=1)
            
            orders = Order.objects.filter(
                shop=self.shop,
                created_at__gte=hour_start,
                created_at__lt=hour_end
            )
            
            completed = orders.filter(status=Order.STATUS_COLLECTED)
            revenue = completed.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
            
            hourly_data.append({
                'hour_start': hour_start,
                'hour_label': hour_start.strftime('%I:%M %p'),
                'total_orders': orders.count(),
                'completed_orders': completed.count(),
                'revenue': revenue
            })
        
        hourly_data.reverse()
        return {'hourly_data': hourly_data}
    
    def get_comprehensive_analytics(self, period_days=30):
        """
        Get all analytics in one comprehensive report
        """
        return {
            'most_ordered': self.get_most_ordered_items(period_days),
            'least_sold': self.get_least_sold_items(period_days),
            'payment_methods': self.get_payment_method_analysis(period_days),
            'peak_hours': self.get_peak_hours_analysis(period_days),
            'daily_report': self.get_daily_report(period_days),
            'weekly_report': self.get_weekly_report(4),
            'monthly_report': self.get_monthly_report(12),
            'hourly_report': self.get_hourly_report(24)
        }
    
    def get_ml_insights(self, period_days=30):
        """
        Machine Learning based insights and recommendations
        """
        from orders.models import Order
        
        insights = []
        
        # Analyze most ordered items
        top_items = self.get_most_ordered_items(period_days, limit=5)
        if top_items:
            top_item = top_items[0]
            insights.append({
                'type': 'success',
                'category': 'Best Seller',
                'message': f"'{top_item['menu_item__name']}' is your best-selling item with {top_item['total_quantity']} orders generating ₹{top_item['total_revenue']:.2f}"
            })
        
        # Analyze least sold items
        least_items = self.get_least_sold_items(period_days, limit=5)
        no_sales_items = [item for item in least_items if item['total_quantity'] == 0]
        if no_sales_items:
            insights.append({
                'type': 'warning',
                'category': 'Inventory Alert',
                'message': f"{len(no_sales_items)} items have zero sales in the last {period_days} days. Consider promoting or removing them."
            })
        
        # Payment method recommendation
        payment_analysis = self.get_payment_method_analysis(period_days)
        if payment_analysis['most_used']:
            insights.append({
                'type': 'info',
                'category': 'Payment Preference',
                'message': f"{payment_analysis['most_used']['percentage']:.1f}% of customers prefer {payment_analysis['most_used']['method']}"
            })
        
        # Peak hour insight
        peak_analysis = self.get_peak_hours_analysis(period_days)
        if peak_analysis['busiest_hour']:
            hour = peak_analysis['busiest_hour']
            insights.append({
                'type': 'info',
                'category': 'Peak Time',
                'message': f"Your busiest hour is {hour['hour_label']} with {hour['count']} orders. Ensure adequate staffing during this time."
            })
        
        # Revenue trend
        daily_report = self.get_daily_report(period_days)
        if daily_report['trend_percentage'] != 0:
            direction = 'increased' if daily_report['trend_direction'] == 'up' else 'decreased'
            insights.append({
                'type': 'success' if daily_report['trend_direction'] == 'up' else 'warning',
                'category': 'Trend Analysis',
                'message': f"Your order volume has {direction} by {abs(daily_report['trend_percentage']):.1f}% compared to the previous week."
            })
        
        return insights
    
    def _get_time_period_label(self, hour):
        """Helper method to label time periods"""
        if 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 21:
            return 'Evening'
        else:
            return 'Night'
