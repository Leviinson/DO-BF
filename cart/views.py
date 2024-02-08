"""Views of the cart."""

import json
from typing import Any

from django.http import HttpRequest, HttpResponse, HttpResponseServerError, JsonResponse

from async_views.generic.base import AsyncTemplateView
from services.common_handlers import common_handlers
from services.data_getters import crm_data
from services.mixins import ApplicationMixin

from .app_services.session_data import session_data
from .app_services.utils import formatters


class CartView(AsyncTemplateView, ApplicationMixin):
    """Class view for process adding product to customer ordered products."""

    http_method_names = ["post", "put", "delete", "get"]
    template_name = "cart/index.html"

    async def get(self, request, *args, **kwargs) -> HttpResponse:
        """Asynchronous variation of GET method."""
        context = await self.get_context_data(**kwargs)
        if isinstance(context, HttpResponseServerError):
            return context
        response = self.render_to_response(context)
        response["Cache-Control"] = "no-store"
        return response

    async def get_context_data(self, **kwargs: Any) -> dict[str, list[dict[str, Any]]]:
        """
        Get context data.

        :param kwargs: any keyword arguments.
        :return: A dictionary containing context data.
        """
        context: dict[str, list[dict[str, Any]]] = await self.get_common_context(
            **await super().get_context_data(**kwargs)
        )
        if isinstance(context, HttpResponseServerError):
            return context
        context["title"] = "Корзина"
        old_cart = await session_data.get_or_create_cart(self.request.session)
        region = context["region"]
        region_products = await self._get_region_products(
            region, context["selected_currency"], old_cart["products"]
        )
        context["cart"] = updated_cart = await self._update_cart_data(region_products, old_cart)

        context["cart_products"] = await formatters.format_cart_products(
            updated_cart,
            region_products,
            context["selected_currency"],
        )
        context["cart_grand_total_price"] = self._calculate_cart_grand_total_price(
            context["cart_products"]
        )
        context["suggested_products"] = await self._get_suggested_products(
            region, region_products, context["cart_products"]
        )
        context["is_cart"] = True
        return context

    async def _update_cart_data(
        self, region_products: list[dict[str, Any]], old_cart: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update cart data in the context.

        :param context: The context dictionary.
        """
        outdated_cart_products_ids = await self._find_outdated_cart_products_ids(
            region_products, old_cart
        )
        await self._remove_outdated_cart_products(outdated_cart_products_ids)
        return await session_data.get_or_create_cart(self.request.session)

    async def _get_region_products(
        self,
        region: dict[str, Any],
        selected_currency: dict[str, str | float],
        cart_products: list[dict[str, int]],
    ) -> list[dict[str, Any]]:
        """
        Get region products based on the provided region and context.

        :param region: The region dictionary.
        :param context: The context dictionary.
        :return: A list of region products.
        """
        return await crm_data.get_region_products(
            region["slug"],
            currency=selected_currency,
            cart_ids_set={product["id"] for product in cart_products},
        )

    async def _find_outdated_cart_products_ids(
        self, region_products: list[dict[str, Any]], cart: dict[str, Any]
    ) -> tuple[dict[str, Any]]:
        """
        Find outdated cart products by comparing region products with the cart.

        :param region_products: list of region products.
        :param cart: The cart dictionary.
        :return: A list of outdated cart product IDs.
        """
        return {
            product["id"]
            for product in cart["products"]
            if product["id"] not in (product["id"] for product in region_products)
        }

    async def _remove_outdated_cart_products(
        self, outdated_cart_products_ids: tuple[str]
    ) -> None:
        """
        Remove outdated cart products from the session.

        :param outdated_cart_products: list of outdated cart product IDs.
        """
        await session_data.remove_ordered_products(
            self.request.session, outdated_cart_products_ids
        )

    async def _get_suggested_products(
        self, region: dict[str, Any], region_products: list[dict[str, Any]], cart_products
    ) -> list[dict[str, Any]]:
        """
        Get suggested products for the given region.

        :param region: The region dictionary.
        :param region_products: list of region products.
        :return: A list of suggested products.
        """
        return await common_handlers.get_first_three_additional_products(
            region["slug"], region_products, cart_products
        )

    def _calculate_cart_grand_total_price(
        self, cart_products: list[dict[str, Any]]
    ) -> float:  # TODO: to combine this method with CheckoutView.calculate_cart_grand_total
        """
        Calculate the grand total price of cart products.

        :param cart_products: list of cart products.
        :return: The grand total price.
        """
        return round(
            sum(
                map(
                    lambda x: (x["unit_price"] if not x["discount"] else x["new_price"])
                    * x["cart_amount"],
                    cart_products,
                )
            ),
            2,
        )

    async def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        """Handle POST request for adding product to customer ordered products."""
        try:
            data: dict = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Wrong data passed"}, status=400)

        if not all([(product_id := data.get("id")), (amount := data.get("amount"))]):
            return JsonResponse({"msg": "Product ID or amount isn't passed"}, status=400)

        if not isinstance(product_id, str):
            return JsonResponse(
                {"msg": "Product ID must be integer reduced to string"}, status=400
            )

        if not product_id.isdigit():
            return JsonResponse(
                {"msg": "Product ID isn't integer reduced to string"}, status=400
            )

        if not isinstance(amount, int):
            return JsonResponse({"msg": "Product amount must be integer"}, status=400)

        bouquet_size = data.get("bouquet_size")
        if bouquet_size:
            if not isinstance(bouquet_size, int):
                return JsonResponse({"msg": "Bouquet size must be integer"}, status=400)
        context: dict[str, list[dict[str, Any]]] = await self.get_common_context(
            *args, **kwargs
        )
        return await session_data.create_ordered_product(
            request,
            request.session,
            product_id,
            amount,
            context["region"],
            bouquet_size,
        )

    async def put(self, request: HttpRequest, *args: Any, **kwargs: dict) -> JsonResponse:
        """Handle PUT request for updating product to customer ordered products."""
        try:
            data: dict = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Wrong data passed"}, status=400)

        if not all([(product_id := data.get("id")), (amount := data.get("amount"))]):
            return JsonResponse({"msg": "Product ID or amount isn't passed"}, status=400)

        if not isinstance(product_id, str):
            return JsonResponse(
                {"msg": "Product ID must be integer reduced to string"}, status=400
            )

        if not product_id.isdigit():
            return JsonResponse(
                {"msg": "Product ID isn't integer reduced to string"}, status=400
            )

        if not isinstance(amount, int):
            return JsonResponse({"msg": "Product amount must be integer"}, status=400)

        bouquet_size = data.get("bouquet_size")
        if bouquet_size:
            if not isinstance(bouquet_size, int):
                return JsonResponse({"msg": "Bouquet size must be integer"}, status=400)
        context: dict[str, list[dict[str, Any]]] = await self.get_common_context(
            *args, **kwargs
        )
        return await session_data.update_ordered_product(
            request, request.session, product_id, amount, context["region"], bouquet_size
        )

    async def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        """Handle Delete request for deleting ordered_products record."""
        try:
            data: dict = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Wrong data passed"}, status=400)

        if not (product_id := data.get("id")):
            return JsonResponse({"msg": "Product ID isn't passed"}, status=400)

        if not isinstance(product_id, str):
            return JsonResponse(
                {"msg": "Product ID must be integer reduced to string"}, status=400
            )

        if not product_id.isdigit():
            return JsonResponse(
                {"msg": "Product ID isn't integer reduced to string"}, status=400
            )

        bouquet_size = data.get("bouquet_size")
        if bouquet_size:
            if not isinstance(bouquet_size, int):
                return JsonResponse({"msg": "Bouquet size must be integer"}, status=400)
        return await session_data.remove_ordered_product(
            request.session, product_id, bouquet_size
        )
