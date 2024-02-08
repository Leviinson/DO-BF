"""Urls list for 'mainpage' app."""
from django.urls import path

from .views import MainPageView

app_name = "main_page"

urlpatterns = [
    path("", MainPageView.as_view(), name="main_page"),
    path("<slug:region_slug>/", MainPageView.as_view(), name="mainpage-view"),
]
