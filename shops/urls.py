from django.urls import path

from .views import (
    analytics_dashboard,
    owner_dashboard, 
    shop_detail, 
    shop_list,
    search_menu,
    manage_menu,
    add_menu_item,
    edit_menu_item,
    delete_menu_item,
    toggle_item_availability,
    add_category,
    edit_category,
    delete_category,
    edit_shop_settings,
)

app_name = "shops"

urlpatterns = [
    path("", shop_list, name="list"),
    path("search/", search_menu, name="search_menu"),
    path("shops/<int:shop_id>/", shop_detail, name="detail"),
    path("owner/dashboard/", owner_dashboard, name="owner_dashboard"),
    path("owner/analytics/", analytics_dashboard, name="analytics"),
    
    # Menu management
    path("owner/menu/", manage_menu, name="manage_menu"),
    path("owner/menu/add/", add_menu_item, name="add_menu_item"),
    path("owner/menu/edit/<int:item_id>/", edit_menu_item, name="edit_menu_item"),
    path("owner/menu/delete/<int:item_id>/", delete_menu_item, name="delete_menu_item"),
    path("owner/menu/toggle/<int:item_id>/", toggle_item_availability, name="toggle_item"),
    
    # Category management
    path("owner/category/add/", add_category, name="add_category"),
    path("owner/category/edit/<int:category_id>/", edit_category, name="edit_category"),
    path("owner/category/delete/<int:category_id>/", delete_category, name="delete_category"),
    
    # Shop settings
    path("owner/settings/", edit_shop_settings, name="edit_shop_settings"),
]
