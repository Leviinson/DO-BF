"""Function and class views list for 'products' app."""
import json
from typing import Any, Set

from django.http import (
    HttpRequest,
    HttpResponseNotFound,
    HttpResponseServerError,
    JsonResponse,
)
from django.views import View

from async_views.generic.base import AsyncTemplateView
from cart.app_services.session_data import session_data
from catalogue.app_services.utils import bread_crumbs
from products.app_services.data_getters import crm_data
from products.app_services.product_handlers import product_detail_handlers
from products.exceptions import BouquetSizeNotFoundError, ProductNotFoundError
from services.data_getters import crm_data as service_crm_data
from services.mixins import ApplicationMixin
from services.utils import utilities
from userprofile.app_services.userprofile_handlers import user_handlers


class ProductView(ApplicationMixin, AsyncTemplateView):
    """Class view for product detail information."""

    template_name = "products/product.html"

    async def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Get the context data for the view.

        Args:
            **kwargs (Any): Additional keyword arguments.

        Returns:
            dict: A dictionary containing the context data.
        """
        context = await self.get_common_context(**await super().get_context_data(**kwargs))
        if isinstance(context, HttpResponseServerError):
            return context
        region_slug, category_slug, subcategory_slug, product_slug = self._get_slugs(
            await service_crm_data.get_subcategories_list(), context
        )
        product_dict = await product_detail_handlers.get_product_details_for_product_view(
            region_slug, subcategory_slug, product_slug, context["selected_currency"]
        )
        self._handle_product_not_found(product_dict)
        cart: dict = await session_data.get_or_create_cart(self.request.session)
        cart_ids_set = {product["id"] for product in cart["products"]}
        region_products = await service_crm_data.get_region_products(
            context["region"]["slug"],
            currency=context["selected_currency"],
            cart_ids_set=cart_ids_set,
        )
        similar_products = await product_detail_handlers.get_first_nine_similar_products(
            region_slug,
            subcategory_slug,
            product_dict.get("id"),
            product_dict.get("bouquet_colors"),
            product_dict.get("bouquet_flowers"),
            product_dict.get("is_bouquet"),
            context["selected_currency"],
            region_products,
        )
        context["category_crumb"] = await bread_crumbs.get_category_crumb(category_slug)
        if self.is_subcat_exists:
            context["subcategory_crumb"] = await bread_crumbs.get_subcategory_crumb(
                subcategory_slug
            )
        context.update(
            self._build_context_data(
                product_dict, similar_products, category_slug, subcategory_slug, product_slug
            )
        )
        await self._refresh_customer_viewed_products(product_dict)
        return context

    async def get(self, request: HttpRequest, *args, **kwargs):
        """
        Handle the HTTP GET request for the product view.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The HTTP response for the request.
        """
        self.is_subcat_exists = await self._check_subcategory_existence(
            await service_crm_data.get_subcategories_list()
        )
        if self.is_subcat_exists:
            try:
                try:
                    context = await self.get_context_data(**kwargs)
                    if isinstance(context, HttpResponseServerError):
                        return context
                except BouquetSizeNotFoundError:
                    return HttpResponseNotFound()
            except ProductNotFoundError:
                return HttpResponseNotFound()

            cart: dict = await session_data.get_or_create_cart(self.request.session)
            if (product := context["product"])["is_bouquet"]:
                try:
                    self._handle_bouquet_size(request, product, context)
                except BouquetSizeNotFoundError:
                    return HttpResponseNotFound()
                for cart_product in cart["products"]:
                    if (
                        cart_product["id"] == context["product"]["id"]
                        and cart_product["size"] == context["selected_bouquet_size"]["value"]
                    ):
                        context["product"]["is_in_cart"] = True
                        context["product"]["cart_amount"] = cart_product["amount"]
                        break
                else:
                    context["product"]["is_in_cart"] = False
            else:
                for cart_product in cart["products"]:
                    if context["product"]["id"] == cart_product["id"]:
                        context["product"]["is_in_cart"] = True
                        context["product"]["cart_amount"] = cart_product["amount"]
                        break
                else:
                    context["product"]["is_in_cart"] = False
            return self.render_to_response(context)
        return HttpResponseNotFound()

    def _get_slugs(self, subcategories_list: list[dict[str, str]], context: dict[str, str]):
        """
        Extract and return region, category, subcategory, and product slugs.

        Args:
            subcategories_list (list[dict[str, str]]): List of subcategories.
            context (dict[str, str]): The context dictionary.

        Returns:
            Tuple: A tuple containing region_slug, category_slug,
            subcategory_slug, and product_slug.
        """
        region_slug = context["region"]["slug"]
        category_slug = next(
            (
                subcat["category_slug"]
                for subcat in subcategories_list
                if subcat["slug"] == self.kwargs["subcategory_slug"]
            ),
            None,
        )
        subcategory_slug = self.kwargs.get("subcategory_slug")
        product_slug = self.kwargs.get("product_slug")
        return region_slug, category_slug, subcategory_slug, product_slug

    def _handle_product_not_found(self, product_dict):
        """
        Raise a ProductNotFoundError if the product is not found.

        Args:
            product_dict: The product dictionary to check.
        """
        if not product_dict:
            raise ProductNotFoundError()

    def _build_context_data(
        self, product_dict, similar_products, category_slug, subcategory_slug, product_slug
    ):
        """
        Build the context data dictionary.

        Args:
            product_dict: The product dictionary.
            similar_products: List of similar products.
            category_slug: The category slug.
            subcategory_slug: The subcategory slug.
            product_slug: The product slug.

        Returns:
            dict: The context data dictionary.
        """
        context_data = {
            "product": product_dict,
            "similar_products": similar_products,
            "title": product_dict.get("Name"),
            "subcategory_slug": subcategory_slug,
            "category_slug": category_slug,
            "product_slug": product_slug,
        }
        return context_data

    async def _refresh_customer_viewed_products(self, product_dict):
        """
        Refresh the customer viewed products in the session.

        Args:
            product_dict: The product dictionary to use for refreshing.
        """
        """
        Check if the subcategory exists in the list.

        Args:
            subcategories_list (list[dict[str, str]]): List of subcategories.

        Returns:
            bool: True if the subcategory exists, otherwise False.
        """
        if product_id := product_dict.get("id"):
            await user_handlers.refresh_customer_viewed_products(
                self.request.session, product_id
            )

    async def _check_subcategory_existence(self, subcategories_list: list[dict[str, str]]):
        """
        Check if the subcategory exists in the list.

        Args:
            subcategories_list (list[dict[str, str]]): List of subcategories.

        Returns:
            bool: True if the subcategory exists, otherwise False.
        """
        subcategory_slug = self.kwargs["subcategory_slug"]
        return subcategory_slug in (subcat["slug"] for subcat in subcategories_list)

    def _handle_bouquet_size(self, request, product, context):
        """
        Handle the selected bouquet size.

        Args:
            request (HttpRequest): The HTTP request object.
            product: The product dictionary.
            context: The context dictionary.

        Returns:
            HttpResponse: The HTTP response for handling the bouquet size.
        """
        if not request.GET.get("size"):
            context["selected_bouquet_size"] = product["bouquet_sizes"][0]

        else:
            for size in product["bouquet_sizes"]:
                if request.GET.get("size") == str(size["value"]):
                    context["selected_bouquet_size"] = size
                    break
            else:
                raise BouquetSizeNotFoundError()


class ProductSearchView(View, ApplicationMixin):
    """
    Class view for searching products.

    Inherits from View.

    Usage:
    To use this view, define the URL pattern in your urls.py and map it to this
    view class. When a GET request is made to the defined URL, this view will search
    for products based on the 'search' query parameter in the request.GET dictionary.
    If the 'search' parameter is present, it will search for products in the region
    determined by self.get_region().
    The search results will be returned as a JSON response.
    If the 'search' parameter is not present, it will redirect to the main_page view.

    Example URL Pattern in urls.py:
    path('product-search/', ProductSearchView.as_view(), name='product_search'),
    """

    async def get(self, request, *args, **kwargs):
        """
        Handle GET request for searching products.

        :param request: The HttpRequest object.
        :param args: Any positional arguments passed to the view.
        :param kwargs: Any keyword arguments passed to the view.

        Returns:
        If the 'search' parameter is present in the request.GET dictionary, it searches
        for products based on the 'search' parameter in the region determined by
        self.get_region(). The search results are returned as a JSON response in the
        format: {"results": [list of searched products]}

        If the 'search' parameter is not present, it redirects to the main_page view
        using HttpResponseRedirect.
        """
        data: dict[str, str] = request.GET
        name = data.get("search")
        subcategory_slug = data.get("subcategory")
        min_budget = data.get("minBudget")
        max_budget = data.get("maxBudget")
        if name and subcategory_slug:
            return JsonResponse({"msg": "Wrong format of parameters"}, status=400)
        elif not name and not subcategory_slug and not min_budget and not max_budget:
            return JsonResponse({"msg": "Required data aren't passed"}, status=400)

        currency_qparam = request.GET.get("currency")
        if not currency_qparam:
            return JsonResponse({"msg": "Currency is not provided"}, status=400)

        context = await self.get_common_context(**kwargs)
        if isinstance(context, HttpResponseServerError):
            return context
        if not context["region"]:
            return JsonResponse({"msg": "Selected region not found"}, status=400)

        cart: dict = await session_data.get_or_create_cart(self.request.session)
        cart_ids_set = {product["id"] for product in cart["products"]}
        return await self.handle_search_request(
            request,
            currency_qparam,
            context["region"],
            name,
            subcategory_slug,
            data.get("minBudget"),
            data.get("maxBudget"),
            cart_ids_set,
        )

    async def handle_search_request(
        self,
        request: HttpRequest,
        currency_qparam: str,
        region: dict[str, str],
        name: str,
        subcategory_slug: str,
        min_budget: Any,
        max_budget: Any,
        cart_ids_set: Set[str],
    ):
        """
        Handle the search request for products.

        :param request: The HttpRequest object.
        :param context: Context data.
        :param search: The search query.

        Returns:
        If successful, returns a JsonResponse with search results and
        selected currency symbol.
        If the 'currency' parameter is missing, returns a JsonResponse with an
        error message and status 400.
        If the selected currency is not found, returns a JsonResponse with an
        error message and status 400.
        """
        if name and not subcategory_slug and min_budget is None and max_budget is None:
            currencies: list[
                dict
            ] | HttpResponseServerError = await service_crm_data.get_currency_list(request)
            if isinstance(currencies, HttpResponseServerError):
                return currencies
            currency = utilities.get_selected_currency(currencies, currency_qparam)

            if not currency:
                return JsonResponse({"msg": "Selected currency not found"}, status=400)

            region_products = await service_crm_data.get_region_products(
                region["slug"], currency=currency, cart_ids_set=cart_ids_set
            )
            searched_products = product_detail_handlers.search_region_products(
                region_products, name
            )
        elif not name and (subcategory_slug or (min_budget and max_budget)):
            min_budget_float, max_budget_float = utilities.get_min_max_budget(
                min_budget, max_budget
            )
            if (
                min_budget_float is None
                or max_budget_float is None
                and (min_budget and max_budget)
            ):
                return JsonResponse(
                    {"msg": 'Min and max budget must be "str reduced to float"/"int".'},
                    status=400,
                )
            currencies = await service_crm_data.get_currency_list(request)
            if isinstance(currencies, HttpResponseServerError):
                return currencies
            currency = utilities.get_selected_currency(currencies, currency_qparam)

            if not currency:
                return JsonResponse({"msg": "Selected currency not found"}, status=400)

            region_products = await service_crm_data.get_region_products(
                region["slug"], currency=currency, cart_ids_set=cart_ids_set
            )
            searched_products = product_detail_handlers.search_region_products(
                region_products,
                name,
                subcategory_slug,
                min_budget_float,
                max_budget_float,
            )

        response_data = {
            "results": searched_products,
        }
        return JsonResponse(response_data, status=200)

    async def put(self, request, *args: Any, **kwargs: dict) -> JsonResponse:
        """Handle PUT request for updating product to customer ordered products."""
        try:
            data: dict = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Wrong data passed"}, status=400)

        if not all([(product_id := data.get("productId")), (amount := data.get("amount"))]):
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

        if ordered_product := await crm_data.get_ordered_product(
            request.user.zoho_id,
            product_id,
        ):
            if product_detail_handlers.update_ordered_product(
                ordered_product["id"],
                amount,
            ):
                return JsonResponse({"msg": "Succesfully updated amount"}, status=204)
        else:
            return JsonResponse({"msg": "Ordered product doesn't exist"}, status=404)

    @staticmethod
    async def delete(request, *args: Any, **kwargs: Any) -> JsonResponse:
        """Handle Delete request for deleting ordered_products record."""
        try:
            data: dict = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Wrong data passed"}, status=400)

        if not (product_id := data.get("productId")):
            return JsonResponse({"msg": "Product ID isn't passed"}, status=400)

        if not isinstance(product_id, str):
            return JsonResponse(
                {"msg": "Product ID must be integer reduced to string"}, status=400
            )

        if not product_id.isdigit():
            return JsonResponse(
                {"msg": "Product ID isn't integer reduced to string"}, status=400
            )

        product_id = int(product_id)
        if ordered_product := await crm_data.get_ordered_product(
            request.user.zoho_id,
            product_id,
        ):
            if product_detail_handlers.delete_ordered_product(ordered_product["id"]):
                return JsonResponse({"msg": "Ordered product deleted"}, status=204)
        return JsonResponse({"msg": "Ordered product doesn't exist"}, status=404)
