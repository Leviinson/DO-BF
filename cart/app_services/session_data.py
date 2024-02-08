"""Represents processing of the session data for the cart."""
from typing import Any, Iterable

from asgiref.sync import sync_to_async
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest, JsonResponse

from products.app_services.data_getters import crm_data as products_crm_data
from services.data_getters import crm_data
from services.utils import utilities


class SessionData:
    """Represents processing of the session data for the cart."""

    @staticmethod
    async def get_or_create_cart(session: SessionBase) -> dict[str, list | int]:
        """
        Get or create the cart from the request's session data.

        Args:
            session (SessionBase): The session to work with.

        Returns:
            dict: The cart data containing products and their quantity.
        """
        if cart := (await sync_to_async(session.get)("cart", {})):
            return cart
        return {"products": [], "quantity": 0}

    @classmethod
    def get_ordered_product(
        cls, cart: dict[str, Any], product_id: str, bouquet_size: int | None
    ) -> dict[str, Any] | None:
        """
        Refresh customer cart.

        Product, if doesn't exist in cart, will be returned.
        :param session: session object.
        :param product_id: str, product id in Zoho CRM module.
        """
        for product in cart["products"]:
            if bouquet_size:
                if product["id"] == product_id and product["size"] == bouquet_size:
                    return product
            else:
                if product["id"] == product_id and not product.get("size"):
                    return product

    @classmethod
    async def create_ordered_product(
        cls,
        request: HttpRequest,
        session: SessionBase,
        product_id: str,
        amount: int,
        region: dict[str, Any],
        bouquet_size: int | None = None,
    ) -> bool:
        """
        Create an ordered product in the session's cart.

        Args:
            session (SessionBase): The session to work with.
            product_id (str): The ID of the product to add.
            amount (int): The quantity of the product to add.

        Returns:
            bool: True if the product was successfully added, False if it already exists.

        This method adds a product to the cart in the provided session. If the product
        already exists in the cart, it won't be added again.
        """
        cart = await cls.get_or_create_cart(session)
        default_currency = utilities.get_selected_currency(
            await crm_data.get_currency_list(request), region["default_currency"]
        )
        region_products = await crm_data.get_region_products(
            region["slug"],
            currency=default_currency,
        )
        if cls.get_ordered_product(cart, product_id, bouquet_size):
            return JsonResponse({"msg": "Already created"}, status=409)
        for product in region_products:
            if product["id"] == product_id and product["category_slug"] == "bouquets":
                if bouquet_size is not None and bouquet_size not in (
                    size_record["value"]
                    for size_record in (
                        await products_crm_data.get_product_bouquet_data(
                            product_id,
                            currency=default_currency,
                            discount=product["discount"],
                        )
                    )["bouquet_sizes"]
                ):
                    return JsonResponse(
                        {"msg": 'Not existing "size" parameter was provided'}, status=404
                    )
                cart["products"].append(
                    {"id": product_id, "size": bouquet_size, "amount": amount}
                )
                break
        else:
            cart["products"].append({"id": product_id, "amount": amount})
        cart["quantity"] += amount
        session["cart"] = cart
        await sync_to_async(session.save)()
        return JsonResponse({"msg": "Succesfully created ordered product"}, status=201)

    @classmethod
    async def update_ordered_product(
        cls,
        request: HttpRequest,
        session: SessionBase,
        product_id: str,
        amount: int,
        region: dict[str, Any],
        bouquet_size: int | None = None,
    ) -> JsonResponse:
        """
        Update the quantity of an ordered product in the session's cart.

        Args:
            session (SessionBase): The session to work with.
            product_id (str): The ID of the product to update.
            amount (int): The new quantity of the product.

        Returns:
            JsonResponse: A JSON response indicating success or failure.

        This method updates the quantity of a product in the cart within the provided session.
        If the product doesn't exist, it won't be updated.
        """
        cart = await cls.get_or_create_cart(session)
        if ordered_product := cls.get_ordered_product(cart, product_id, bouquet_size):
            default_currency = utilities.get_selected_currency(
                await crm_data.get_currency_list(request), region["default_currency"]
            )
            region_products = await crm_data.get_region_products(
                region["slug"],
                currency=default_currency,
            )

            if bouquet_size is not None:
                for product in region_products:
                    if product["id"] == product_id and product["category_slug"] == "bouquets":
                        if bouquet_size not in (
                            size_record["value"]
                            for size_record in (
                                await products_crm_data.get_product_bouquet_data(
                                    product_id,
                                    currency=default_currency,
                                    discount=product["discount"],
                                )
                            )["bouquet_sizes"]
                        ):
                            # TODO: removing of bouquets with deprecated sizes from the cart
                            return JsonResponse(
                                {"msg": 'Not existing "size" parameter was provided'},
                                status=404,
                            )
                        break
            ordered_product["amount"] = amount
            cart["quantity"] = sum(i["amount"] for i in cart["products"])
            session["cart"] = cart
            await sync_to_async(session.save)()
            return JsonResponse({"msg": "Succesfully updated amount"}, status=204)
        return JsonResponse({"msg": "Ordered product doesn't present in the cart."}, status=404)

    @classmethod
    async def remove_ordered_product(
        cls, session: SessionBase, product_id: str, bouquet_size: int | None
    ) -> JsonResponse:
        """
        Remove an ordered product from the session's cart.

        Args:
            session (SessionBase): The session to work with.
            product_id (str): The ID of the product to remove.

        Returns:
            bool: True if the product was successfully removed, False if it doesn't exist.

        This method removes a product from the cart in the provided session. If the product
        doesn't exist in the cart, it won't be removed.
        """
        cart = await cls.get_or_create_cart(session)
        if ordered_product := cls.get_ordered_product(cart, product_id, bouquet_size):
            response = JsonResponse({"msg": "Ordered product deleted"}, status=204)
            cart["quantity"] -= ordered_product["amount"]
            cart["products"].remove(ordered_product)
            session["cart"] = cart
            await sync_to_async(session.save)()
            return response
        return JsonResponse({"msg": "Ordered product doesn't present in the cart."}, status=404)

    @classmethod
    async def remove_ordered_products(
        cls, session: SessionBase, products_ids: Iterable[str]
    ) -> JsonResponse:
        """
        Remove an ordered product from the session's cart.

        Args:
            session (SessionBase): The session to work with.
            product_id (str): The ID of the product to remove.

        Returns:
            bool: True if the product was successfully removed, False if it doesn't exist.

        This method removes a product from the cart in the provided session. If the product
        doesn't exist in the cart, it won't be removed.
        """
        cart = await cls.get_or_create_cart(session)
        cart["products"] = [p for p in cart["products"] if p["id"] not in products_ids]
        cart["quantity"] = sum(i["amount"] for i in cart["products"])
        session["cart"] = cart
        await sync_to_async(session.save)()

    @staticmethod
    async def add_order(session: SessionBase, order_id: str):
        """
        Add an order to the session.

        Args:
            session (SessionBase): The session to work with.
            order_id (str): The ID of the order to add.

        Returns:
            None

        This static method adds an order to the session. If the session already has
        orders, the new order ID is appended to the existing list of orders. If there
        are no existing orders, a new list containing the provided order ID is created.
        The session is then saved asynchronously.
        """
        if session.get("orders"):
            session["orders"].append(order_id)
            await sync_to_async(session.save)()
        else:
            session["orders"] = [
                order_id,
            ]
            await sync_to_async(session.save)()

    @staticmethod
    async def get_client_orders_id_list(session: SessionBase):
        """
        Retrieve the list of order IDs associated with the client's session.

        Args:
            session (SessionBase): The session to retrieve order IDs from.

        Returns:
            List[str]: A list of order IDs. If no orders are present, an empty list is returned.

        This static method retrieves the list of order IDs associated with the provided
        client session. If the session has orders, the list of order IDs is returned.
        If there are no orders, an empty list is returned.
        """
        return await sync_to_async(session.get)("orders", [])


session_data = SessionData()

{
    "products": {
        "321": [{"amount": 2}],
        "123": [{"size": 54, "amount": 3}, {"size": 25, "amount": 1}],
        "15": [{"size": 60, "amount": 5}],
    }
}
