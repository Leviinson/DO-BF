"""Urls list for 'userprofile' app."""

from django.urls import path

from .views import CartView

app_name = "cart"

urlpatterns = [
    path("<slug:region_slug>/cart/", CartView.as_view(), name="cart"),
]
