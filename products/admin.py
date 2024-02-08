"""Admin site configuration for 'product' app."""

import shutil
from datetime import datetime, timedelta

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from products.models import ZohoImage, ZohoModuleRecord


class ZohoModuleRecordAdmin(admin.ModelAdmin):
    """ZohoModuleRecord admin site settings."""

    list_display = (
        "id",
        "module_name",
        "record_name",
        "accessed_at",
    )
    list_display_links = (
        "id",
        "module_name",
        "record_name",
    )
    actions = ["clean_product_records"]

    @admin.action(
        description="Delete all product records and its images" "older than 3 months."
    )
    def clean_product_records(
        self,
        request: HttpRequest,
        queryset: QuerySet,
    ) -> None:
        """Delete instances and files in media with accessed_at older than 3 months."""
        instances = ZohoModuleRecord.objects.filter(
            accessed_at__lte=(datetime.now() - timedelta(days=90))
        ).defer("accessed_at")
        for instance in instances:
            shutil.rmtree(f"media/{instance.module_name}/{instance.record_name}")
        instances.delete()


class ZohoImageAdmin(admin.ModelAdmin):
    """ZohoImage admin site settings."""

    list_display = (
        "id",
        "zoho_record",
        "image",
    )
    list_display_links = (
        "id",
        "zoho_record",
    )


admin.site.register(ZohoModuleRecord, ZohoModuleRecordAdmin)
admin.site.register(ZohoImage, ZohoImageAdmin)
