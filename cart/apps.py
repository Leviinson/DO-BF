"""Application config module."""
from django.apps import AppConfig


class CartConfig(AppConfig):
    """Cart config class."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "cart"
