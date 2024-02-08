"""Contains common handlers classes."""

import random
from typing import Any

from cart.app_services.utils import formatters as cart_formatters
from services.data_getters import crm_data


class CommonHandlers:
    """Contains common handlers."""

    @staticmethod
    async def get_first_three_additional_products(
        region_slug: str,
        region_products: list[dict[str, Any]],
        cart_products: list[dict[str, Any]],
    ) -> list:
        """
        Get first three additional products from random subcategory 'Present' category.

        WARNING: There is hardcoded name of the "Presents" module in the ZohoCRM.

        :param region_slug: str
        """
        filtered_subcategories_slugs = [
            subcategory["slug"]
            for subcategory in await crm_data.get_subcategories_list()
            if subcategory["category_name"] == "Подарки"
        ]

        filtered_additional_products = [
            product
            for product in region_products
            if product["region_slug"] == region_slug
            and product["subcategory_slug"] in filtered_subcategories_slugs
            and product["id"] not in (product["id"] for product in cart_products)
        ]
        if len(filtered_additional_products) >= 4:
            additional_products = random.sample(
                filtered_additional_products,
                4,
            )
        else:
            additional_products = filtered_additional_products
        return additional_products

    @staticmethod
    async def get_cart_products(
        region_slug: str, cart: dict[str, Any], currency: dict[str, float]
    ):
        """
        Update the context with cart-related data.

        Args:
            context (dict): The context dictionary.
        """
        region_products = await crm_data.get_region_products(
            region_slug,
            currency=currency,
            cart_ids_set={product["id"] for product in cart["products"]},
        )
        return await cart_formatters.format_cart_products(cart, region_products, currency)


common_handlers = CommonHandlers()
