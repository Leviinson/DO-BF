"""Module, that contains caching operations."""
from typing import Optional

from django.core.cache import cache
from django.http import HttpRequest, HttpResponseServerError
from django.shortcuts import render

from mainpage.models import Contact

from .crm_entities_handlers import (
    categories_handler,
    currency_handler,
    region_products_handler,
    regions_default_currencies_handler,
    regions_handler,
    subcategories_handler,
)
from .utils import convert_products_prices, ip_geo_locator, mark_products_in_cart


class crm_data:
    """Class with methods for getting and setting data from cache."""

    @staticmethod
    async def get_location(ip_address: str) -> dict:
        """
        Get the locality information using the given IP address.

        Args:
            ip_address (str): The IP address.

        Returns:
            Dict: The locality information.
        """
        if location_data := cache.get(f"{ip_address}"):
            return location_data
        location_data: dict = await ip_geo_locator.fetch_location(ip_address)
        cache.set(f"{ip_address}", location_data, 10)
        return location_data

    @staticmethod
    async def get_regions_list(request: HttpRequest) -> list[dict[str, str]]:
        """
        Get the region dictionary by fetching them from the cache or Zoho CRM.

        The dictionary has names as keys and slugs as values.

        Returns:
            Dict: The region dictionary.
        """
        if value := cache.get("region_dict"):
            return value
        region_dict: dict = await regions_handler.fetch_instances()
        if not region_dict:
            return HttpResponseServerError(
                render(
                    request,
                    "templates/notification.html",
                    {
                        "header": "Server error",
                        "message_top": "We are so sorry, but the shop isn't \
                            initialized properly (empty regions)",
                        "message_bottom": "You can notify an owner about it",
                        "redirect_link": ".",
                        "redirect_message": "Repeat",
                    },
                ),
                status=503,
            )
        cache.set("region_dict", region_dict, 10)
        return region_dict

    @staticmethod
    async def get_regions_default_currencies() -> dict | list:
        """
        Get the dict of regions default currencies.

        The region slug as key, currency name as value.

        Returns:
            Union[Dict, List]: The regions currencies dictionary or empty list.
        """
        if value := cache.get("regions_default_currencies"):
            return value
        regions_default_currencies_dict = (
            await regions_default_currencies_handler.fetch_instances()
        )
        cache.set("regions_default_currencies", regions_default_currencies_dict, 10)
        return regions_default_currencies_dict

    @staticmethod
    @convert_products_prices
    @mark_products_in_cart
    async def get_region_products(
        region_slug: str,
        currency: dict[str, str | int],
        cart_ids_set: Optional[set[str]] = None,
    ) -> list[dict[str, str]]:
        """
        Get region products from Zoho CRM or cache.

        :param region_code: str The region for the request.
        :param currency: dict Currency dict.
        :param cart_ids_set: Optional set with cart product ids.

        Returns:
            List: The region products.
        """
        if region_products := cache.get(f"{region_slug}_products"):
            return region_products
        subcategories_list = await crm_data.get_subcategories_list()
        region_products: list = await region_products_handler.fetch_instances(
            region_slug, currency=currency, subcategories=subcategories_list
        )
        cache.set(f"{region_slug}_products", region_products, 10)
        return region_products

    @staticmethod
    async def get_currency_list(request: HttpRequest) -> list[dict[str, str]] | list:
        """Get currency list from cache or Zoho CRM."""
        if currency_list := cache.get("currency_list"):
            return currency_list
        currency_list: list = await currency_handler.fetch_instances()
        if not currency_list:
            return HttpResponseServerError(
                render(
                    request,
                    "templates/notification.html",
                    {
                        "header": "Server error",
                        "message_top": "We are so sorry, but the shop isn't \
                            initialized properly (empty currencies)",
                        "message_bottom": "You can notify an owner about it",
                        "redirect_link": ".",
                        "redirect_message": "Repeat",
                    },
                ),
                status=503,
            )
        cache.set("currency_list", currency_list, 10)
        return currency_list

    @staticmethod
    async def get_subcategories_list() -> list[dict[str, str]]:
        """
        Get subcategories information from the cache or Zoho CRM.

        Returns:
            List: The subcategories information.
        """
        if subcategories := cache.get("subcategories"):
            return subcategories
        subcategories: list = await subcategories_handler.fetch_instances()
        cache.set("subcategories", subcategories, 10)
        return subcategories

    @staticmethod
    async def get_categories_list() -> list[dict[str, str]]:
        """
        Get categories information from the cache or Zoho CRM.

        Returns:
            List: The categories information.
        """
        if categories := cache.get("categories"):
            return categories
        categories: list = await categories_handler.fetch_instances()
        cache.set("categories", categories, 10)
        return categories

    @staticmethod
    async def get_contacts() -> Contact:
        """
        Get contact information from the cache or local database.

        Returns:
            Contact: The contact information.
        """
        if contacts := cache.get("contacts"):
            return contacts
        contacts: Contact = await Contact.objects.afirst()
        cache.set("contacts", contacts, 10)
        return contacts

    @staticmethod
    def search_region_products(search: str, region_products: list) -> list[dict[str, str]]:
        """
        Fetch products data from Zoho CRM using search query.

        :param search: sent searching data.
        :param region_products: region for current request;
        """
        searched_products: list = []
        searched_products_ids_set: set = set()
        for product in region_products:
            if product["Name"].lower() == search.lower():
                searched_products.append(product)
                searched_products_ids_set.add(product["id"])
        searched_products += [
            product
            for product in region_products
            if product["Name"].lower().find(search.lower()) != -1
            and product["id"] not in searched_products_ids_set
        ]
        return searched_products


crm_data = crm_data()
