"""Urls for 'catalogue' app."""

from django.urls import path

from .views import CatalogueView

app_name = "catalogue"

urlpatterns = [
    path(
        "<slug:region_slug>/<slug:category_slug>/",
        CatalogueView.as_view(),
        name="category_view",
    ),
    path(
        "<slug:region_slug>/<slug:category_slug>/<slug:subcategory_slug>/",
        CatalogueView.as_view(),
        name="subcategory_view",
    ),
]
