"""Module for getting data for 'mainpage' app."""
from typing import List

from mainpage.app_services.crm_entities_handlers import additional_products_handler


class CRMData:
    """Class with methods for getting data."""

    @staticmethod
    async def get_additional_products(region_slug: str, subcategories_string: str) -> List:
        """
        Get additional products list from Zoho CRM.

        Parameters
        :param region_slug: str
        :param subcategories_string: str

        Returns
        Products list.
        """
        return await additional_products_handler.fetch_instances(
            region_slug, subcategories_string
        )


crm_data = CRMData()
