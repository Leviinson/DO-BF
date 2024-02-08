"""Module for getting data for 'userprofile' app."""
from typing import Dict, List, Optional

from services.utils import convert_products_prices
from userprofile.app_services.crm_enitites_handlers import (
    customer_address_handler,
    customer_addresses_handler,
    customer_contact_handler,
    customer_contacts_handler,
    customer_default_address_handler,
    customer_viewed_products_handler,
)


class CRMData:
    """Class with methods for getting data."""

    @staticmethod
    async def get_customer_addresses(customer_id: int) -> List:
        """
        Get customer addresses data list from Zoho CRM.

        :param customer_id: int Customers module record id.
        """
        return await customer_addresses_handler.fetch_instances(customer_id)

    @staticmethod
    async def get_customer_address(address_id: int) -> Dict:
        """
        Get address data by id from Zoho CRM.

        :param address_id: int Record id in Zoho CRM module.
        """
        return await customer_address_handler.fetch_instance(address_id)

    @staticmethod
    async def get_customer_default_address(customer_id: int) -> Dict:
        """
        Get address data by id from Zoho CRM.

        :param customer_id: int Record id in Zoho CRM module.
        """
        return await customer_default_address_handler.fetch_instance(customer_id)

    @staticmethod
    async def get_customer_contacts(customer_id: int) -> List:
        """
        Get contacts data by customer id in Zoho CRM module.

        :param customer_id: int Record id in Zoho CRM module.
        """
        return await customer_contacts_handler.fetch_instances(customer_id)

    @staticmethod
    async def get_customer_contact(contact_id: int) -> Dict:
        """
        Get customer contact data by id from Zoho CRM.

        :param contact_id: int Contact id in Zoho CRM module.
        """
        return await customer_contact_handler.fetch_instance(contact_id)

    @staticmethod
    @convert_products_prices
    async def get_customer_viewed_product_list(
        products_ids: List,
    ) -> List[Optional[Dict]]:
        """
        Get product data list from Zoho CRM by given ids list.

        :param products_ids: list Product ids in Zoho CRM module.
        """
        ids_string = str(products_ids[0])
        for product_id in products_ids[1:50]:
            ids_string += f", {product_id}"
        return await customer_viewed_products_handler.fetch_instances(ids_string)


crm_data = CRMData()
