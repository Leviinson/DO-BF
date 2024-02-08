"""Module with utilities for 'userprofile' app."""
from typing import Dict, List

from zcrmsdk.src.com.zoho.crm.api.record import Record

from services.data_getters import crm_data


class CRMFormatters:
    """Class for Zoho CRM formatting functionality."""

    @staticmethod
    def prepare_address_contact_creation_data(data: Dict, customer_id: int) -> Dict:
        """
        Prepare data dict for Zoho CRM customer address creation.

        :param data: dict Dict with data received from AddressForm.
        :param customer_id: int Customer id in Zoho CRM module.
        """
        data["Name"] = data.pop("name")
        record = Record()
        record.set_id(customer_id)
        data["customer_id"] = record
        return data

    @staticmethod
    async def modify_products_dicts_list(products: List[Dict]) -> List[Dict]:
        """
        Modify products dicts keys for using in django templates.

        :param products: list[dict] Products dicts list.
        """
        subcategories_list = await crm_data.get_subcategories_list()
        for product in products:
            product["region_slug"] = product.pop("region_id.slug")
            product["subcategory_slug"] = product.pop("subcategory_id.slug")
            product["category_slug"] = next(
                (
                    subcategory["category_slug"]
                    for subcategory in subcategories_list
                    if subcategory["slug"] == product["subcategory_slug"]
                ),
                None,
            )
        return products


crm_formatters = CRMFormatters()
