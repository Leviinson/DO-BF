"""Module for getting data for 'product' app."""
from typing import Any, Dict, List

from django.core.cache import cache

from products.app_services.crm_entities_handlers import (
    first_nine_similar_bouquets_handler,
    ordered_product_handler,
    product_bouquet_handler,
    product_details_handler,
)
from services.utils import (
    convert_bouquet_sizes_prices,
    convert_product_price,
    convert_products_prices,
)


class CRMData:
    """Class with methods for getting data."""

    @staticmethod
    @convert_product_price
    async def get_product_details(
        region_slug: str,
        subcategory_slug: str,
        product_slug: str,
        currency: dict[str, str | float],
    ) -> Dict:
        """
        Get product details, using region, subcategory and product slugs.

        :param region_slug: str Region slug.
        :param subcategory_slug: str Subcategory slug.
        :param product_slug: str Product slug.
        """
        if product_data := cache.get(
            f"{product_slug}_product"
        ):  # TODO: create 'get_or_set_cache' function
            return product_data
        product_data = await product_details_handler.fetch_instance(
            region_slug, subcategory_slug, product_slug, currency=currency, is_many=True
        )
        if product_data:
            cache.set(f"{product_slug}_product", product_data, 3600)
        return product_data

    @staticmethod
    @convert_bouquet_sizes_prices
    async def get_product_bouquet_data(
        product_id: int, currency: dict[str, str], discount: float | None
    ) -> Dict:
        """Get bouquet and bouquet size data for product using id."""
        if bouquet_data := cache.get(f"{product_id}_bouquet"):
            return bouquet_data
        bouquet_data: dict = await product_bouquet_handler.fetch_instances(product_id)
        cache.set(f"{product_id}_bouquet", bouquet_data, 3600)
        return bouquet_data

    @staticmethod
    @convert_products_prices
    async def get_first_nine_similar_bouquets(
        region_slug: str, product_id: str, **kwargs: Any
    ) -> List:
        """
        Get Zoho CRM region products bouquets.

        Products sorted by is_recommended, discount.
        :param region_slug: str Region slug.
        :param product_id: str Product id.
        """
        if similar_bouquets := cache.get(f"{product_id}_similar_bouquets"):
            return similar_bouquets
        similar_bouquets = await first_nine_similar_bouquets_handler.fetch_instances(
            region_slug, product_id, **kwargs
        )
        cache.set(f"{product_id}_similar_bouquets", similar_bouquets, 3600)
        return similar_bouquets

    @staticmethod
    async def get_ordered_product(customer_id: int, product_id: int) -> Dict:
        """
        Get Zoho CRM ordered_products instance.

        :param customer_id: int Ordered_products instance customer_id.
        :param product_id: int Ordered_products instance product id.
        """
        return await ordered_product_handler.fetch_instance(customer_id, product_id)


crm_data = CRMData()
