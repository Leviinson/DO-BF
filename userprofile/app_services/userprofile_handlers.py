"""Module for userprofile additional functionality."""
from typing import Set

from asgiref.sync import sync_to_async
from django.contrib.sessions.backends.base import SessionBase

from services.data_getters import crm_data


class UserHandlers:
    """Class for methods with additional functionality."""

    @staticmethod
    async def refresh_customer_viewed_products(session: SessionBase, product_id: str) -> None:
        """
        Refresh customer product list.

        Product, if doesn't exist in list, will be added, otherwise 'viewed_at'
        field will be updated.
        :param customer: User User object in local db table.
        :param product_id: int Product id in Zoho CRM module.
        """
        if not await sync_to_async(session.get)("viewed_products", []):
            session["viewed_products"] = [
                product_id,
            ]
        elif len(viewed_products := session.get("viewed_products")) < 3 and (
            product_id not in session.get("viewed_products", [])
        ):
            viewed_products.append(product_id)
            await sync_to_async(session.save)()

    async def get_and_refresh_viewed_customer_products(
        self,
        session: SessionBase,
        region_slug: str,
        currency: dict[str, str | int],
        cart_ids_set: Set[str],
    ) -> list[dict[str, str]]:
        """
        Get viewed customer product list.

        Get products ids from local db, fetch products data from Zoho CRM by them,
        clean products ids list in local db in case if some ids is not present in
        Zoho CRM, return sorted product list by 'viewed_at' field.
        :param customer_id: int Customer id in local db.
        """
        if viewed_products := await sync_to_async(session.get)("viewed_products", []):
            region_products = await crm_data.get_region_products(
                region_slug=region_slug,
                currency=currency,
                cart_ids_set=cart_ids_set,
            )
            for product_id in viewed_products:
                if product_id not in [product["id"] for product in region_products]:
                    session["viewed_products"].remove(product_id)
            return [product for product in region_products if product["id"] in viewed_products]
        return []


user_handlers = UserHandlers()
