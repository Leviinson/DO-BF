"""Admin site configuration for 'mainpage' app."""


from django.contrib import admin
from django.http.request import HttpRequest

from .models import Contact, CustomCategories, MainSlider, SeoBlock


class ContactAdmin(admin.ModelAdmin):
    """Contacts admin site settings."""

    list_display = ("international_phone_number",)
    list_display_links = ("international_phone_number",)


class SeoBlockAdmin(admin.ModelAdmin):
    """SeoBlock admin site settings."""

    list_display = ("id", "description")
    list_display_links = ("id", "description")


class MainSliderAdmin(admin.ModelAdmin):
    """Mainslider admin site settings."""

    def get_readonly_fields(self, request: HttpRequest, obj: MainSlider):
        """To disallow set up link if it's the first slide."""
        if obj and obj.ordinal_number == 1:
            return ("link",)
        return super().get_readonly_fields(request, obj)


admin.site.register(Contact, ContactAdmin)
admin.site.register(SeoBlock, SeoBlockAdmin)
admin.site.register(MainSlider, MainSliderAdmin)
admin.site.register(CustomCategories)
