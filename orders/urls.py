from django.urls import path

from .views import (
    add_to_cart,
    cancel_order,
    checkout,
    extend_pickup_time,
    feedback_list,
    order_list,
    remove_from_cart,
    submit_feedback,
    update_cart_qty,
    update_status,
    view_cart,
)

app_name = "orders"

urlpatterns = [
    path("cart/", view_cart, name="cart"),
    path("cart/add/<int:item_id>/", add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", update_cart_qty, name="update_cart_qty"),
    path("cart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path("checkout/", checkout, name="checkout"),
    path("my/", order_list, name="list"),
    path("cancel/<int:order_id>/", cancel_order, name="cancel"),
    path("extend/<int:order_id>/", extend_pickup_time, name="extend_pickup_time"),
    path("feedback/<int:order_id>/", submit_feedback, name="submit_feedback"),
    path("feedbacks/", feedback_list, name="feedback_list"),
    path("status/<int:order_id>/", update_status, name="update_status"),
]
