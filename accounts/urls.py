from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    EmailLoginView, UserLoginView, ShopOwnerLoginView, 
    register, register_shop_owner, login_selection, logout_view,
    notification_list, mark_notification_read, mark_all_notifications_read, get_unread_count,
    profile_view, change_password
)

app_name = "accounts"

urlpatterns = [
    # Registration & Authentication
    path("register/", register, name="register"),
    path("register/shop-owner/", register_shop_owner, name="register_shop_owner"),
    path("login/", login_selection, name="login"),
    path("login/user/", UserLoginView.as_view(), name="login_user"),
    path("login/owner/", ShopOwnerLoginView.as_view(), name="login_owner"),
    path("logout/", logout_view, name="logout"),
    
    # Password Management
    path("password-reset/", 
         auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
         name="password_reset"),
    path("password-reset/done/", 
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"),
         name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", 
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"),
         name="password_reset_confirm"),
    path("password-reset-complete/", 
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"),
         name="password_reset_complete"),
    path("change-password/", change_password, name="change_password"),
    
    # Profile & Notifications
    path("profile/", profile_view, name="profile"),
    path("notifications/", notification_list, name="notifications"),
    path("notifications/<int:notification_id>/read/", mark_notification_read, name="mark_notification_read"),
    path("notifications/mark-all-read/", mark_all_notifications_read, name="mark_all_read"),
    path("api/notifications/unread-count/", get_unread_count, name="unread_count"),
]
