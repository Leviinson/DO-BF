"""Feedback urls."""
from django.urls import path

from .views import LocationView

app_name = "location"

urlpatterns = [
    path("location/", LocationView.as_view(), name="location-view"),
]
