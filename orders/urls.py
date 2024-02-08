"""Orders urls."""
from django.urls import path

from .views import CheckoutView, IndividualOrders, OrdersList, QuickOrders

app_name = "orders"

urlpatterns = [
    path(
        "individual-orders/",
        IndividualOrders.as_view(),
        name="individual-order",
    ),
    path(
        "quick-orders/",
        QuickOrders.as_view(),
        name="quick-order",
    ),
    path("<slug:region_slug>/checkout/", CheckoutView.as_view(), name="checkout"),
    path("<slug:region_slug>/orders/", OrdersList.as_view(), name="orders-list"),
]
