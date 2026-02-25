from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages

from .forms import LoginForm, RegistrationForm, ShopOwnerRegistrationForm
from .models import Notification


def logout_view(request):
    """Custom logout view that handles both GET and POST"""
    logout(request)
    return redirect('shops:list')


def login_selection(request):
    """Select login type - User or Shop Owner"""
    if request.user.is_authenticated:
        return redirect("shops:list")
    return render(request, "accounts/login_selection.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("shops:list")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("shops:list")

    return render(request, "accounts/register.html", {"form": form})


def register_shop_owner(request):
    """Register a new shop owner with their shop"""
    if request.user.is_authenticated:
        return redirect("shops:list")

    form = ShopOwnerRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("shops:owner_dashboard")

    return render(request, "accounts/register_shop_owner.html", {"form": form})


class UserLoginView(LoginView):
    """Login view for college users"""
    template_name = "accounts/login_user.html"
    authentication_form = LoginForm
    
    def form_valid(self, form):
        """Override to check if user is a college user"""
        user = form.get_user()
        
        # Check if user has profile and is a college user
        if hasattr(user, 'profile'):
            if user.profile.role != 'college_user':
                messages.error(
                    self.request, 
                    'Access denied. This login is for college users only. Shop owners should use the shop owner login.'
                )
                return self.form_invalid(form)
        
        # If valid, proceed with login
        return super().form_valid(form)
    
    def get_success_url(self):
        return "/orders/my/" if hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'college_user' else "/"


class ShopOwnerLoginView(LoginView):
    """Login view for shop owners"""
    template_name = "accounts/login_owner.html"
    authentication_form = LoginForm
    
    def form_valid(self, form):
        """Override to check if user is a shop owner"""
        user = form.get_user()
        
        # Check if user has profile and is a shop owner
        if hasattr(user, 'profile'):
            if user.profile.role != 'shop_owner':
                messages.error(
                    self.request, 
                    'Access denied. This login is for shop owners only. College users should use the student login.'
                )
                return self.form_invalid(form)
        else:
            messages.error(
                self.request, 
                'Access denied. This account does not have shop owner privileges.'
            )
            return self.form_invalid(form)
        
        # If valid, proceed with login
        return super().form_valid(form)
    
    def get_success_url(self):
        return "/owner/dashboard/" if hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'shop_owner' else "/"


# Keep for backward compatibility
class EmailLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm


@login_required
def notification_list(request):
    """View all notifications for the current user"""
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, "accounts/notifications.html", {
        "notifications": notifications,
        "unread_count": unread_count
    })


@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read and redirect to its link"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    
    # Redirect to the notification's link if it exists, otherwise to notifications list
    if notification.link:
        return redirect(notification.link)
    return redirect("accounts:notifications")


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("accounts:notifications")


@login_required
def get_unread_count(request):
    """API endpoint to get unread notification count"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"unread_count": count})


@login_required
def profile_view(request):
    """View and edit user profile"""
    profile = getattr(request.user, 'profile', None)
    
    return render(request, "accounts/profile.html", {
        "user": request.user,
        "profile": profile
    })


@login_required
def change_password(request):
    """Allow users to change their password"""
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    from django.contrib import messages
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})
