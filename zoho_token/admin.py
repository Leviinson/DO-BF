"""Admin site configuration for 'zoho_token' app."""

from django.contrib import admin

from .models import ZohoOAuth


class ZohoOAuthAdmin(admin.ModelAdmin):
    """ZohoOAuth admin site settings."""

    list_display = ("id", "user_email", "client_id")
    list_display_links = ("id", "user_email")


admin.site.register(ZohoOAuth, ZohoOAuthAdmin)
