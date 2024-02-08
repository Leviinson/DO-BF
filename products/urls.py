"""Urls for 'products' app."""

from django.urls import path

from .views import ProductSearchView, ProductView

app_name = "products"

urlpatterns = [
    path(
        "<slug:region_slug>/",
        ProductSearchView.as_view(),
    ),
    path(
        "<slug:region_slug>/<slug:subcategory_slug>/<slug:product_slug>/",
        ProductView.as_view(),
        name="product",
    ),
]
