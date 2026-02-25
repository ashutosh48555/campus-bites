from django.urls import path

from .views import toggle_availability

app_name = "menu"

urlpatterns = [
    path("items/<int:item_id>/toggle/", toggle_availability, name="toggle_availability"),
]
