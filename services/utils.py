"""Contains rare-used utils."""

import inspect
import os
from collections import defaultdict
from functools import wraps
from typing import Any, Optional

import httpx
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse_lazy
from dotenv import load_dotenv

from mainpage.models import Contact

load_dotenv()


class IPGeoLocator:
    """Defines user location by IP, uses 'ipapi' API."""

    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        """
        Get ip from request META info.

        :param request: Django HttpRequest instance.
        """
        if x_forwarded_for := request.META.get("HTTP_X_FORWARDED_FOR"):
            return x_forwarded_for.split(",")[-1].strip()
        elif ip := request.META.get("HTTP_X_REAL_IP"):
            return ip
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    async def fetch_location(ip_address: str) -> dict[str, str]:  # TODO async
        """
        Fetch local ip address data.

        :param ip_address: str ip_address.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"https://ipapi.co/{ip_address}/json/?key={os.getenv('IP_API_KEY')}"
            )
        if response.content:
            response = response.json()
        return {
            "ip": ip_address,
            "city": response.get("city"),
            "region": response.get("region"),
            "country": response.get("country_name"),
        }


ip_geo_locator = IPGeoLocator()


class Formatters:
    """Class with methods for formatting messages."""

    @staticmethod
    def modify_subcategories(subcategories: list[dict[str, int]]) -> list[dict[str, int]]:
        """
        Modify fetch Zoho categories to more convenient structure.

        :param subcategories: list with categories and subcategories data.
        """
        for item in subcategories:
            item["id"] = int(item["id"])
            item["category_id"] = item.pop("category_id.id")
            item["category_slug"] = item.pop("category_id.slug")
            item["category_name"] = item.pop("category_id.Name")
        return subcategories

    @staticmethod
    def format_categories_and_related_subcategories(
        categories: list[dict[str, list]], subcategories: list[dict[str, str]]
    ) -> list[dict[str, list]]:
        #   TODO Return value in docstrings doesn't correspond to the actual return,
        #   should be refactored or deleted
        """
        To format dict of categories and relatedsubcategories list.

        Returns:
        [{'id': 134343,
          'Name': 'Букеты',
          'slug': 'bouquets',
          'subcategories': [{'id': 11, 'Name': 'Миксы', 'slug': 'mixes'},
                            {'id': 12, 'Name': 'Элитные', 'slug': 'elite'}]},
         {'id': 134333,
          'Name': 'Подарки',
          'slug': 'presents',
          'subcategories': [{'id': 3, 'Name': 'Игрушки', 'slug': 'toys'},
                            {'id': 4, 'Name': 'Шарики', 'slug': 'balloons'}]}]
        """
        subcategories_dict = defaultdict(list)
        for subcategory in subcategories:
            subcategories_dict[subcategory["category_slug"]].append(subcategory)
        for category in categories:
            category["subcategories"] = subcategories_dict[category["slug"]]
        return categories

    @staticmethod
    async def format_regions_list(regions: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        Create dict with regions codes and slugs as keys and values.

        :param regions: List Regions data from Zoho CRM.
        """
        for region in regions:
            region["city"] = region.pop("Name")
            region["default_currency"] = region.pop("country_id.currency_id.Name")
            region["email"] = region.pop("Email")
            region["country_code"] = region.pop("country_id.code")
            region["international_phone_number"] = (
                await Contact.objects.afirst()
            ).international_phone_number
            region["country_name"] = region.pop("country_id.Name")
        return regions

    async def format_product_list(self, products: list[dict[str, str]], **kwargs) -> list[dict]:
        """
        Modify fetch Zoho products to more convenient structure.

        :param products: list[dict] List for products dicts.
        """
        subcategory_dict: dict = {
            sub["slug"]: sub.get("category_slug") for sub in kwargs.get("subcategories", [])
        }
        for product in products:
            product["discount"] = 0 if not product.get("discount") else product.get("discount")
            region_slug = product["region_slug"] = product.pop("region_id.slug")
            product["subcategory_name"] = product.pop("subcategory_id.Name")
            subcat_slug = product["subcategory_slug"] = product.pop("subcategory_id.slug")
            product["category_slug"] = subcategory_dict.get(product["subcategory_slug"])
            product_slug = product["slug"]
            product["url"] = reverse_lazy(
                "products:product",
                kwargs={
                    "region_slug": region_slug,
                    "subcategory_slug": subcat_slug,
                    "product_slug": product_slug,
                },
            )
        return products

    @staticmethod
    def format_regions_default_currencies(data: list) -> dict:
        """
        Return list of default currencies of the regions.

        Returns dict like one:
        {"dnipro": "UAH", "delmenhorst": "EUR"}
        """
        return {region["slug"]: region["default_currency"] for region in data}

    @staticmethod
    def format_user_data(data: dict[str, str]) -> dict:
        """Modify given dict keys to correspond with Zoho CRM module keys."""
        return {
            "Email": data.get("email"),
            "Name": data.get("username"),
            "phone_number": data.get("phone_number"),
        }


formatters = Formatters()


class Utilities:
    """
    Utility class for common functions.

    This class provides utility functions for common tasks.

    Methods:
    - get_selected_currency(
        currencies: list[lict],
        selected_currency_name: str
    ) -> Union[dict, None]:
        Get the selected currency from the list of currencies.

    - get_min_max_budget() -> Union[Union[float, None],
                              Union[float, None]]:
        Parse the minimum and maximum budget values.

    """

    @staticmethod
    def get_selected_currency(
        currencies: list[dict[str, str]], selected_currency_name: str
    ) -> dict | None:
        """
        Get the selected currency from the context.

        :param currencies: currencies list.
        :param selected_currency_name: The selected currency query parameter.

        Returns:
        The selected currency if found, otherwise None.
        """
        return next(
            (
                currency
                for currency in currencies
                if currency["Name"].lower() == selected_currency_name.lower()
            ),
            None,
        )

    @staticmethod
    def get_min_max_budget(
        min_budget: str | None, max_budget: str | None
    ) -> tuple[float | None, float | None]:
        """
        To parse the minimum and maximum budget from the data.

        :param min_budget: str digit or None.
        :param max_budget: str digit or None.

        Returns:
        A tuple containing the minimum (or None) and maximum (or None)
        budgets as float values.
        """
        try:
            if min_budget and max_budget:
                return float(min_budget), float(max_budget)
            elif max_budget:
                return None, float(max_budget)
            elif min_budget:
                return float(min_budget), None
            return None, None
        except ValueError:
            return None, None


utilities = Utilities()


def convert_products_prices(func):
    """
    To wrap to convert the prices of a list of products to the selected currency.

    Args:
        func (callable): The original function to be wrapped.

    Returns:
        callable: A wrapped function that converts product prices.

    """

    @wraps(func)
    async def wrap(*args, **kwargs):
        """
        TO wrap the original function to convert prices of a list of products.

        Args:
            *args: Variable positional arguments to be passed to the original function.
            **kwargs: Variable keyword arguments to be passed to the original function,
            including 'currency'.

        Returns:
            list: The list of products with converted prices.

        """
        if inspect.iscoroutinefunction(func):
            products = await func(*args, **kwargs)
        else:
            products = func(*args, **kwargs)
        currency = kwargs["currency"]
        for product in products:
            convert_price(product, currency, product.get("discount"))
        return products

    return wrap


def convert_product_price(func):
    """
    To wrap to convert the price of a single product to the selected currency.

    Args:
        func (callable): The original function to be wrapped.

    Returns:
        callable: A wrapped function that converts a product's price.

    """

    @wraps(func)
    async def wrap(*args, **kwargs):
        """
        To wrap the original function to convert the price of a single product.

        Args:
            *args: Variable positional arguments to be passed to the original function.
            **kwargs: Variable keyword arguments to be passed to the original function,
            including 'currency'.

        Returns:
            dict: The product with the converted price.

        """
        if inspect.iscoroutinefunction(func):
            product = await func(*args, **kwargs)
        else:
            product = func(*args, **kwargs)
        currency = kwargs["currency"]
        convert_price(product, currency, product.get("discount"))
        return product

    return wrap


def convert_price(
    product: dict[str, Any],
    currency: dict[str, Any],
    discount: Optional[float],
    price_key: str = "unit_price",
) -> None:
    """
    To convert the price of a product to the selected currency.

    Args:
        product (dict[str, Any]): The product to be modified with the converted price.
        currency (dict[str, Any]): The currency information used for conversion.
        discount (optional[float]): Discount rate if it is.
        price_key (str): Price key to fetch price from dict.

    Returns:
        None

    """
    product[price_key] = round(float(product[price_key]) / currency["static_exchange_rate"], 2)
    if discount:
        product["new_price"] = round((product[price_key] * (100 - discount)) / 100, 2)
    product["currency_symbol"] = currency["symbol"]


def convert_bouquet_sizes_prices(func):
    """
    To wrap to convert the prices of bouquet sizes to the selected currency.

    Args:
        func (callable): The original function to be wrapped.

    Returns:
        callable: A wrapped function that converts bouquet size prices.

    """

    @wraps(func)
    async def wrap(*args, **kwargs):
        bouquet_data = await func(*args, **kwargs)
        currency = kwargs.get("currency")
        discount = kwargs.get("discount")
        for size in bouquet_data["bouquet_sizes"]:
            convert_price(size, currency, discount, "price")
        return bouquet_data

    return wrap


def mark_products_in_cart(func):
    """
    To decorate function to mark products in the cart.

    Args:
    - func (Callable): The function to be decorated.

    Returns:
    - Callable: The decorated function.
    """

    @wraps(func)
    async def wrap(*args, **kwargs):
        """
        To wrapp function to add 'is_in_cart' key to products.

        Args:
        - args (List): List of positional arguments.
        - kwargs (dict): Dictionary of keyword arguments.

        Returns:
        - list[dict[str, Any]]: List of products marked if they are in the cart.
        """
        products = await func(*args, **kwargs)
        cart_ids_set = kwargs.get("cart_ids_set")
        for product in products:
            product["is_in_cart"] = bool(cart_ids_set) and product["id"] in cart_ids_set
        return products

    return wrap
