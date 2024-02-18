"""Urls list for 'filters' app."""
from django.urls import path

from .views import AboutUsView, ContactsView, DeliveryView

app_name = "fillers"

urlpatterns = [
    path("<slug:region_slug>/about/", AboutUsView.as_view(), name="about"),
    path("<slug:region_slug>/delivery/", DeliveryView.as_view(), name="delivery"),
    path("<slug:region_slug>/contacts/", ContactsView.as_view(), name="contacts"),
]
