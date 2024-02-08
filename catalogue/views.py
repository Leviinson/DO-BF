"""Function and class views list for 'catalogue' app."""

from typing import Any, Dict

from django.core.paginator import Paginator
from django.http import HttpResponseNotFound, HttpResponseServerError

from async_views.generic.base import AsyncTemplateView
from cart.app_services.session_data import session_data
from services.data_getters import crm_data
from services.mixins import ApplicationMixin
from userprofile.app_services.userprofile_handlers import user_handlers

from .app_services.utils import bread_crumbs, filters


# Create your views here.
class CatalogueView(ApplicationMixin, AsyncTemplateView):
    """
    View class for rendering the catalogue page with product listings.

    Extends `ApplicationMixin` and `AsyncTemplateView`.

    Attributes:
        template_name (str): The name of the template to be rendered.

    Dependencies:
        - ApplicationMixin: Provides common functionality for the view.
        - AsyncTemplateView: Django's class-based async view for rendering templates.
    """

    template_name = "catalogue/catalogue.html"

    def __init__(self) -> None:
        """To initiate CatalogueView class."""
        super().__init__()
        self.is_cat_exists = False
        self.is_subcat_exists = False

    async def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Override the base method to get the context data for rendering the template.

        Returns:
            Dict[str, Any]: A dictionary containing the context data for the template.
        """
        context = await self.get_common_context(
            **await super().get_context_data(**kwargs),
        )
        if isinstance(context, HttpResponseServerError):
            return context
        cat_slug = self.kwargs.get("category_slug")
        subcat_slug = self.kwargs.get("subcategory_slug")

        context["category_crumb"] = await bread_crumbs.get_category_crumb(cat_slug)
        if self.is_subcat_exists:
            context["subcategory_crumb"] = await bread_crumbs.get_subcategory_crumb(subcat_slug)

        cart: dict = await session_data.get_or_create_cart(self.request.session)
        cart_products_id_list = {product["id"] for product in cart["products"]}
        filtered_products_by_cat_and_subcat = await filters.filter_products(
            context["region"],
            cat_slug,
            subcat_slug,
            context["selected_currency"],
            self.request.GET.get("sort"),
            cart_ids_set=cart_products_id_list,
        )
        #   TODO check if it will be convinient to change list to set
        context["sort"] = self.request.GET.get("sort")
        paginator = Paginator(filtered_products_by_cat_and_subcat, per_page=2)  # TODO return 12
        page_number = self.request.GET.get("page")
        page = paginator.get_page(page_number)
        context["products_page"] = page
        context[
            "viewed_products"
        ] = await user_handlers.get_and_refresh_viewed_customer_products(
            self.request.session,
            context["region"]["slug"],
            context["selected_currency"],
            cart_products_id_list,
        )
        return context

    async def get(self, request, *args, **kwargs: Dict):
        """Async implementation of the GET-method (for async get_context_data using)."""
        self.is_cat_exists = self.kwargs.get("category_slug") in (
            cat["slug"] for cat in await crm_data.get_categories_list()
        )

        if self.is_cat_exists:
            if subcat_kwarg := self.kwargs.get("subcategory_slug"):
                self.is_subcat_exists = subcat_kwarg in (
                    subcat["slug"] for subcat in await crm_data.get_subcategories_list()
                )
                if self.is_subcat_exists:
                    context = await self.get_context_data(**kwargs)
                    if isinstance(context, HttpResponseServerError):
                        return context
                    return self.render_to_response(context)
                return HttpResponseNotFound()
            return self.render_to_response(await self.get_context_data(**kwargs))
        return HttpResponseNotFound()
