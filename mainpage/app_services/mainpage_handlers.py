"""Handlers for 'mainpage' app."""
from typing import Any


class Utilities:
    """Utilities for ProductsOperations class."""

    @staticmethod
    def get_region_bestsellers(region_products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Get region products bestsellers from Zoho CRM or cache.

        :param region_products: region for current request.
        """
        return [product for product in region_products if product["is_recommended"]]


utilities = Utilities()
