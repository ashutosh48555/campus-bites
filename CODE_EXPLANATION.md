# Complete Code Explanation - Django Food Ordering Application

## 📚 Table of Contents
1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Core Configuration Files](#core-configuration-files)
4. [Applications Deep Dive](#applications-deep-dive)
5. [Database Models](#database-models)
6. [Views and Business Logic](#views-and-business-logic)
7. [URL Routing](#url-routing)
8. [Templates](#templates)
9. [Forms](#forms)
10. [Authentication & Authorization](#authentication--authorization)

---

## Project Overview

This is a **Django-based food ordering system** for college campuses where:
- **Shop Owners** can manage their shops, menus, and orders
- **College Users** can browse shops, order food, and provide feedback
- Real-time notifications, analytics, and payment tracking

### Django MTV Architecture
Django follows **MTV (Model-Template-View)** pattern:
- **Model**: Database structure (what data to store)
- **Template**: HTML presentation (what users see)
- **View**: Business logic (how to process requests)

---

## Project Structure

```
shopapp/
├── campus-bites/              # Main project configuration
├── accounts/           # User authentication & profiles
├── shops/              # Shop management
├── menu/               # Menu items & categories
├── orders/             # Order processing
├── payments/           # Payment handling
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── media/              # User uploads
├── manage.py           # Django management script
├── db.sqlite3          # SQLite database
└── requirements.txt    # Python dependencies
```

---

## Core Configuration Files

### 1. `manage.py` - Django Command Line Tool

```python
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus-bites.settings")
```

**What it does:**
- Entry point for Django commands
- `python manage.py runserver` - Starts development server
- `python manage.py migrate` - Updates database
- `python manage.py createsuperuser` - Creates admin account

**Syntax Breakdown:**
- `os.environ.setdefault()` - Sets environment variable
- `DJANGO_SETTINGS_MODULE` - Tells Django where settings are
- `execute_from_command_line()` - Runs Django management commands

---

### 2. `campus-bites/settings.py` - Global Configuration

**Key Sections Explained:**

#### a) Security Settings
```python
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
```
- `SECRET_KEY`: Used for cryptographic signing (sessions, cookies)
- `DEBUG`: When True, shows detailed errors (NEVER use in production)
- `os.getenv()`: Reads from environment variables (safer than hardcoding)

#### b) Installed Apps
```python
INSTALLED_APPS = [
    "django.contrib.admin",        # Admin interface
    "django.contrib.auth",         # User authentication
    "django.contrib.contenttypes", # Content type framework
    "django.contrib.sessions",     # Session management
    "django.contrib.messages",     # Flash messages
    "django.contrib.staticfiles",  # Static file serving
    "accounts",                    # Your custom apps
    "shops",
    "menu",
    "orders",
    "payments",
]
```
- Built-in Django apps provide core functionality
- Your custom apps extend Django with business logic

#### c) Middleware (Request/Response Pipeline)
```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",           # Security headers
    "django.contrib.sessions.middleware.SessionMiddleware",   # Manages sessions
    "django.middleware.common.CommonMiddleware",              # Common HTTP features
    "django.middleware.csrf.CsrfViewMiddleware",             # CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware", # User authentication
    "django.contrib.messages.middleware.MessageMiddleware",    # Flash messages
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Clickjacking protection
]
```
**How Middleware Works:**
Request → Security → Sessions → CSRF → Auth → Your View → Response

#### d) Database Configuration
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Database type
        "NAME": BASE_DIR / "db.sqlite3",         # Database file location
    }
}
```
- SQLite: File-based database (good for development)
- Production often uses PostgreSQL or MySQL

#### e) Authentication Settings
```python
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", 
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
```
- Enforces strong passwords (8+ chars, not common, not all numbers)

#### f) Session Security
```python
SESSION_COOKIE_AGE = 86400              # 24 hours in seconds
SESSION_COOKIE_HTTPONLY = True          # No JavaScript access
SESSION_COOKIE_SECURE = not DEBUG       # HTTPS only in production
SESSION_COOKIE_SAMESITE = 'Lax'        # CSRF protection
```
- `HTTPONLY`: Prevents XSS attacks
- `SECURE`: Ensures cookies only sent over HTTPS
- `SAMESITE`: Prevents CSRF attacks

#### g) Static & Media Files
```python
STATIC_URL = "static/"                   # URL prefix for static files
STATICFILES_DIRS = [BASE_DIR / "static"] # Development static files
STATIC_ROOT = BASE_DIR / "staticfiles"   # Production collected files

MEDIA_URL = "media/"                     # URL prefix for user uploads
MEDIA_ROOT = BASE_DIR / "media"          # Where uploads are stored
```

---

### 3. `campus-bites/urls.py` - URL Routing (Main Router)

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),           # Admin panel
    path("", include("shops.urls")),           # Shop URLs
    path("accounts/", include("accounts.urls")), # Account URLs
    path("menu/", include("menu.urls")),       # Menu URLs
    path("orders/", include("orders.urls")),   # Order URLs
    path("payments/", include("payments.urls")), # Payment URLs
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**How URL Routing Works:**
1. User visits: `http://localhost:8000/orders/cart/`
2. Django checks `urlpatterns` top to bottom
3. Finds `path("orders/", include("orders.urls"))`
4. Forwards to `orders/urls.py` looking for `cart/`
5. Calls the matched view function

**Syntax:**
- `path(route, view)`: Maps URL pattern to view
- `include()`: Delegates to another URL config
- `<int:id>`: URL parameter (captures integers)
- `<str:slug>`: URL parameter (captures strings)

---

## Applications Deep Dive

### App 1: `accounts/` - User Management

#### `accounts/models.py` - User Data Structure

```python
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("college_user", "College User"),
        ("shop_owner", "Shop Owner"),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    college_name = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
```

**Syntax Breakdown:**

1. **Field Types:**
   - `OneToOneField`: 1-to-1 relationship (each User has one Profile)
   - `CharField`: Text field with max length
   - `max_length=20`: Maximum characters allowed
   - `choices=ROLE_CHOICES`: Dropdown with predefined options
   - `blank=True`: Field can be empty

2. **on_delete=models.CASCADE:**
   - When User is deleted, delete associated Profile too
   - Other options: `SET_NULL`, `PROTECT`, `DO_NOTHING`

3. **__str__ method:**
   - How object appears in admin panel and shell
   - Returns human-readable representation

#### `accounts/views.py` - Request Handlers

**Example View Breakdown:**

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def profile_view(request):
    # Get user's profile
    profile = getattr(request.user, 'profile', None)
    
    # Prepare context data
    context = {
        "user": request.user,
        "profile": profile
    }
    
    # Render template with data
    return render(request, "accounts/profile.html", context)
```

**Syntax Explained:**

1. **@login_required** (Decorator):
   - Function wrapper that checks if user is logged in
   - Redirects to login page if not authenticated
   - Located at settings.py `LOGIN_URL`

2. **request object:**
   - `request.user`: Current logged-in user
   - `request.method`: "GET" or "POST"
   - `request.POST`: Form data submitted
   - `request.GET`: URL query parameters
   - `request.session`: User's session data

3. **getattr(object, 'attribute', default):**
   - Safely gets object attribute
   - Returns `default` if attribute doesn't exist
   - Prevents `AttributeError`

4. **render(request, template, context):**
   - Combines template with data
   - Returns HTTP response
   - `context`: Dictionary of variables for template

5. **redirect(url_name):**
   - Returns HTTP redirect response
   - Sends user to different page

**Form Handling Example:**

```python
def change_password(request):
    if request.method == 'POST':
        # Form submitted
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Password updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct errors.')
    else:
        # Display empty form
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})
```

**Flow:**
1. GET request → Display empty form
2. POST request → Process submitted data
3. Valid → Save and redirect
4. Invalid → Show errors

#### `accounts/decorators.py` - Custom Access Control

```python
from functools import wraps
from django.http import HttpResponseForbidden

def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            profile = getattr(request.user, "profile", None)
            if profile is None or profile.role not in roles:
                return HttpResponseForbidden("Access denied.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def shop_owner_required(view_func):
    return role_required(["shop_owner"])(view_func)
```

**Python Concepts:**

1. **Decorator Pattern:**
   - Function that wraps another function
   - Adds functionality without modifying original function
   - `@wraps`: Preserves original function metadata

2. **Closure:**
   - Inner function accessing outer function's variables
   - `decorator` is closure over `roles`
   - `wrapper` is closure over `view_func`

3. **Usage:**
```python
@shop_owner_required
def owner_dashboard(request):
    # Only shop owners can access this
    pass
```

---

### App 2: `shops/` - Shop Management

#### `shops/models.py` - Shop Data

```python
from django.conf import settings
from django.db import models

class Shop(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["name"]
    
    def __str__(self):
        return self.name
```

**Field Types Explained:**

1. **ForeignKey:**
   - Many-to-one relationship
   - Many shops → One owner
   - `settings.AUTH_USER_MODEL`: References User model (best practice)

2. **TextField:**
   - Unlimited text (rendered as `<textarea>`)
   - Good for long descriptions

3. **EmailField:**
   - CharField with email validation
   - Ensures valid email format

4. **DateTimeField:**
   - Stores date and time
   - `auto_now_add=True`: Set on creation only
   - `auto_now=True`: Update on every save

5. **Meta class:**
   - Model metadata
   - `ordering`: Default sort order for queries
   - `verbose_name`: Human-readable name

#### `shops/views.py` - Shop Business Logic

**Query Example:**

```python
def shop_list(request):
    query = request.GET.get('q', '').strip()
    shops = Shop.objects.all()
    
    if query:
        shops = shops.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    shops = shops.order_by("name")
    return render(request, "shops/shop_list.html", {"shops": shops})
```

**Django ORM Explained:**

1. **Shop.objects.all():**
   - Returns QuerySet of all Shop objects
   - Lazy evaluation (doesn't hit DB until needed)

2. **.filter():**
   - Filters QuerySet
   - Returns new QuerySet
   - Can be chained: `.filter().filter().order_by()`

3. **Q objects:**
   - Complex queries with OR/AND
   - `Q(name__icontains=query)`: Name contains query (case-insensitive)
   - `|`: OR operator
   - `&`: AND operator

4. **Field Lookups:**
   - `field__exact`: Exact match
   - `field__icontains`: Case-insensitive contains
   - `field__gte`: Greater than or equal
   - `field__lt`: Less than
   - `field__in`: In list

**Advanced Query Example:**

```python
from django.db.models import Count, Sum, Avg

def analytics_dashboard(request):
    shop = get_object_or_404(Shop, owner=request.user)
    
    # Aggregate functions
    total_revenue = Order.objects.filter(
        shop=shop,
        status=Order.STATUS_COLLECTED
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    avg_rating = Feedback.objects.filter(
        shop=shop
    ).aggregate(avg=Avg('rating'))['avg'] or 0
```

**Aggregation Functions:**
- `Sum()`: Total of all values
- `Avg()`: Average of values
- `Count()`: Number of records
- `Max()`, `Min()`: Maximum/minimum values

---

### App 3: `menu/` - Menu Management

#### `menu/models.py`

```python
class Category(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ["shop", "name"]

class MenuItem(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="menu_items/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
```

**Key Concepts:**

1. **unique_together:**
   - Database constraint
   - Same category name cannot exist twice for same shop
   - Different shops can have same category names

2. **DecimalField:**
   - Precise decimal numbers (essential for money)
   - `max_digits=8`: Total digits (12345.67 = 7 digits)
   - `decimal_places=2`: Digits after decimal

3. **ImageField:**
   - FileField with image validation
   - Requires Pillow library
   - `upload_to`: Subdirectory in MEDIA_ROOT

4. **BooleanField:**
   - True/False value
   - `default=True`: Initial value for new records

5. **on_delete=models.SET_NULL:**
   - When Category deleted, set foreign key to NULL
   - Requires `null=True`

---

### App 4: `orders/` - Order Processing

#### `orders/models.py` - Complex Relations

```python
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("collected", "Collected"),
        ("cancelled", "Cancelled"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    token_number = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "token_number"],
                name="unique_token_per_shop"
            ),
        ]
    
    def save(self, *args, **kwargs):
        if self.token_number is None:
            self.token_number = random.randint(1000, 9999)
        super().save(*args, **kwargs)
```

**Advanced Concepts:**

1. **choices Parameter:**
   - Creates dropdown in admin/forms
   - First value: stored in database
   - Second value: displayed to users

2. **UniqueConstraint:**
   - Database-level constraint
   - Ensures combination is unique
   - Token numbers unique per shop (not globally)

3. **save() Override:**
   - Custom logic when saving
   - Auto-generate token if not set
   - `super().save()`: Call parent's save method

4. **Many-to-Many through Model:**

```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
```

- **related_name="items":**
  - Access from other side: `order.items.all()`
  - Without it: `order.orderitem_set.all()`

- **on_delete=models.PROTECT:**
  - Prevent deletion if referenced
  - Can't delete MenuItem if it's in an order

**Database Relationships:**
```
User ─────┐
          ├──→ Order ──→ OrderItem ──→ MenuItem
Shop ─────┘
```

#### `orders/views.py` - Session Management

```python
CART_SESSION_KEY = "cart_items"

def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    cart = request.session.get(CART_SESSION_KEY, {})
    
    # Add or increment item
    cart[str(item_id)] = cart.get(str(item_id), 0) + 1
    
    # Save to session
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True
    
    return redirect("shops:detail", shop_id=item.shop_id)
```

**Session Concepts:**

1. **request.session:**
   - Dictionary-like object
   - Stores data between requests
   - Saved in database/cookies

2. **session.modified = True:**
   - Forces session save
   - Needed when modifying mutable objects (dict, list)

3. **Session Storage:**
   - Keys must be strings
   - Values: pickable Python objects
   - Default: database-backed sessions

**Transaction Example:**

```python
from django.db import transaction

@transaction.atomic
def checkout(request):
    # All or nothing - if error, rollback everything
    order = Order.objects.create(...)
    
    for item_id, quantity in cart.items():
        OrderItem.objects.create(
            order=order,
            menu_item_id=item_id,
            quantity=quantity
        )
    
    # Clear cart
    request.session.pop(CART_SESSION_KEY)
```

**@transaction.atomic:**
- Database transaction wrapper
- All queries succeed or all rollback
- Ensures data consistency

---

### App 5: `payments/` - Payment Tracking

```python
class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("online", "Online"),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    payment_status = models.CharField(max_length=10)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
```

---

## Templates Deep Dive

### Template Syntax Basics

**Variables:**
```django
{{ variable_name }}
{{ user.username }}
{{ order.total_price|floatformat:2 }}
```

**Template Filters:**
- `|floatformat:2`: Format as decimal (2 places)
- `|date:"F d, Y"`: Format date
- `|default:"N/A"`: Default if empty
- `|length`: Get length
- `|upper`: Uppercase

**Template Tags:**
```django
{% if user.is_authenticated %}
    Welcome, {{ user.username }}!
{% else %}
    Please login.
{% endif %}

{% for item in items %}
    {{ item.name }}
{% empty %}
    No items found.
{% endfor %}

{% url 'shops:detail' shop.id %}
{% csrf_token %}
```

**Template Inheritance:**

`base.html` (Parent):
```django
<!DOCTYPE html>
<html>
<head>
    <title>Campus Bites</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

`shop_list.html` (Child):
```django
{% extends "base.html" %}

{% block content %}
    <h1>Shop List</h1>
    ...
{% endblock %}
```

---

## Forms Deep Dive

### `forms.py` - Form Classes

```python
from django import forms

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.RadioSelect(),
            "comment": forms.Textarea(attrs={"rows": 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].required = True
```

**Form Concepts:**

1. **ModelForm:**
   - Automatically creates form from model
   - Handles validation
   - `fields`: Which model fields to include

2. **widgets:**
   - How field is rendered in HTML
   - `RadioSelect()`: Radio buttons
   - `Textarea()`: Multi-line text box
   - `Select()`: Dropdown

3. **Form Validation:**
```python
def clean_email(self):
    email = self.cleaned_data['email']
    if User.objects.filter(email=email).exists():
        raise forms.ValidationError("Email already exists")
    return email
```

---

## Authentication Flow

### Login Process

```
User submits login form
    ↓
View receives POST data
    ↓
AuthenticationForm validates
    ↓
authenticate() checks credentials
    ↓
login() creates session
    ↓
Redirect to dashboard
```

### Permission Checking

```python
@login_required
@shop_owner_required
def owner_dashboard(request):
    # 1. Check if logged in (@login_required)
    # 2. Check if shop owner (@shop_owner_required)
    # 3. Execute view
    pass
```

---

## Key Python Concepts Used

### 1. **List Comprehension**
```python
cart_items = [int(qty) for qty in cart.values()]
```

### 2. **Dictionary Methods**
```python
cart.get(item_id, 0)  # Get with default
cart.pop(key, None)   # Remove and return
```

### 3. **String Formatting**
```python
f"Order {self.id} - {self.shop.name}"
```

### 4. **Context Managers**
```python
with transaction.atomic():
    # Code here
```

### 5. **Exception Handling**
```python
try:
    order = Order.objects.get(id=order_id)
except Order.DoesNotExist:
    raise Http404("Order not found")
```

---

## Database Queries Reference

### Creating Objects
```python
shop = Shop.objects.create(name="Pizza Place", owner=user)
```

### Retrieving Objects
```python
Shop.objects.all()                    # All shops
Shop.objects.get(id=1)               # Single shop (raises error if not found)
Shop.objects.filter(owner=user)      # Multiple shops
Shop.objects.first()                 # First object or None
```

### Updating Objects
```python
shop.name = "New Name"
shop.save()

# Bulk update
Shop.objects.filter(owner=user).update(is_active=True)
```

### Deleting Objects
```python
shop.delete()
Shop.objects.filter(is_active=False).delete()
```

### Related Objects
```python
user.shop_set.all()          # All shops owned by user
order.items.all()            # All items in order
shop.menuitem_set.filter()   # Menu items for shop
```

---

## Common Patterns

### 1. **Get Object or 404**
```python
shop = get_object_or_404(Shop, id=shop_id)
# Instead of:
try:
    shop = Shop.objects.get(id=shop_id)
except Shop.DoesNotExist:
    raise Http404()
```

### 2. **Select Related (Performance)**
```python
# Bad (N+1 queries)
orders = Order.objects.all()
for order in orders:
    print(order.shop.name)  # Extra query for each order

# Good (2 queries)
orders = Order.objects.select_related('shop').all()
for order in orders:
    print(order.shop.name)  # No extra query
```

### 3. **Prefetch Related**
```python
shops = Shop.objects.prefetch_related('menuitem_set').all()
# Fetches all menu items in one additional query
```

---

## Security Best Practices (Implemented)

1. **CSRF Protection**: `{% csrf_token %}` in all forms
2. **SQL Injection**: ORM prevents (don't use raw SQL)
3. **XSS Protection**: Django auto-escapes template variables
4. **Password Hashing**: Django uses PBKDF2 by default
5. **Session Security**: HTTP-only cookies, secure in production
6. **Permission Checks**: Decorators on views

---

## Next Steps to Learn

1. **Django Admin**: Customize admin interface
2. **Class-Based Views**: Alternative to function views
3. **Django Signals**: Post-save hooks
4. **Celery**: Background tasks
5. **REST Framework**: Build APIs
6. **Testing**: Write unit tests

---

This guide covers the fundamental concepts. Each file works together to create a complete web application following Django's "Don't Repeat Yourself" (DRY) principle.
