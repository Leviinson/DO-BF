"""Module for general data mixins for 'API' project."""
from typing import Any, Optional

from asgiref.sync import sync_to_async
from django.http import HttpRequest, HttpResponseServerError

from config.constants import Constants
from mainpage.models import CustomCategories
from services.client_handlers import client_handler
from services.data_getters import crm_data
from services.utils import formatters, utilities


class ApplicationMixin:
    """Mixin with data fetching in every view."""

    def __init__(self) -> None:
        """Initialize the ApplicationMixin object."""
        self.kwargs: Optional[dict] = None
        self.request: Optional[HttpRequest] = None

    @staticmethod
    def get_region(
        regions: list[dict[str, str]], slug: str = Constants.DEFAULT_REGION_SLUG
    ) -> dict | None:
        """
        Return the region with the specified slug, or None if not found.

        If 'slug' is provided, it searches for a region with that slug in the 'regions' list.
        If 'slug' is not provided, it tries to define user region by ip.

        Args:
            regions (list[dict[str, str]]): List of regions.
            slug (str): The slug to search for.

        Returns:
            dict | None: A region dictionary or None if not found.
        """
        return next((region for region in regions if region["slug"].lower() == slug), None)

    async def get_common_context(self, **context: dict[str, Any]) -> dict[str, Any]:
        """
        To fetch general context variables.

        This method populates the 'context' dictionary with the following data:
        - 'region'
        - 'currencies'
        - 'selected_currency'
        - 'categories'
        - 'custom_categories'

        Args:
            **context (Any): Additional context data.

        Returns:
            Dict: The context dictionary.
        """
        regions = await crm_data.get_regions_list(self.request)
        if isinstance(regions, HttpResponseServerError):
            return regions
        context = await self.__get_selected_region(context, regions)
        context = await self.__get_selected_currency(self.request, context, regions)
        if isinstance(context, HttpResponseServerError):
            return context
        self.__process_selected_currency(context)
        context = await self.__get_categories(context)
        context["cart_products_quantity"] = (
            await sync_to_async(self.request.session.get)("cart", {})
        ).get("quantity", 0)
        return context

    def __process_selected_currency(self, context):
        """
        Process the selected currency in the context.

        This method checks if 'selected_currency' is present in the context and
        removes it from 'currencies'.
        If 'selected_currency' is not present, it raises an HttpResponseBadRequest.

        Args:
            context (Dict): The context dictionary.
        """
        if not context.get("selected_currency"):
            raise HttpResponseServerError()
        context["currencies"].remove(context["selected_currency"])

    async def __get_selected_region(self, context, regions):
        """
        Get the selected region and set it in the 'context' dictionary.

        Args:
            context: The context dictionary.
            regions: List of regions.

        Returns:
            Dict: The updated context dictionary.
        """
        if region_slug := context.get("region_slug"):
            context["region"] = self.get_region(regions, region_slug)
        else:
            context["region"] = await client_handler.get_client_region(self.request, regions)
        if not context.get("region"):
            context["region"] = self.get_region(regions)
        return context

    async def __get_selected_currency(self, request: HttpRequest, context, regions):
        """
        Get the selected currency and set it in the 'context' dictionary.

        Args:
            context: The context dictionary.

        Returns:
            Dict: The updated context dictionary.
        """
        currencies = context["currencies"] = await crm_data.get_currency_list(request)
        if isinstance(currencies, HttpResponseServerError):
            return currencies

        if selected_currency_name_qparam := self.request.GET.get("currency"):
            context["selected_currency"] = utilities.get_selected_currency(
                currencies, selected_currency_name_qparam
            )
        if not context.get("selected_currency"):
            default_regions_currencies = formatters.format_regions_default_currencies(regions)
            context["selected_currency"] = utilities.get_selected_currency(
                currencies, default_regions_currencies.get(context["region"]["slug"])
            )
        return context

    @staticmethod
    async def __get_categories(context):
        """
        Get categories and related subcategories and set them in the 'context' dictionary.

        Args:
            context: The context dictionary.

        Returns:
            Dict: The updated context dictionary.
        """
        categories = context[
            "categories"
        ] = formatters.format_categories_and_related_subcategories(
            await crm_data.get_categories_list(), await crm_data.get_subcategories_list()
        )
        if (cat_len := len(categories)) < 6:
            context["custom_categories"] = await sync_to_async(list)(
                CustomCategories.objects.all()[: 6 - cat_len]
            )
        return context
