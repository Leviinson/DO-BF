"""Function and class views list for 'mainpage' app."""

import asyncio
from typing import Any

from asgiref.sync import sync_to_async
from django.http import HttpResponseServerError
from django.shortcuts import render

from async_views.generic.base import AsyncTemplateView
from cart.app_services.session_data import session_data
from mainpage.models import MainSlider, SeoBlock
from services.common_handlers import common_handlers
from services.data_getters import crm_data
from services.mixins import ApplicationMixin

from .app_services.mainpage_handlers import utilities


class MainPageView(ApplicationMixin, AsyncTemplateView):
    """Class view mixin for region page."""

    template_name = "mainpage/index.html"

    async def get_context_data(self, **kwargs: Any) -> dict:
        """
        Get context data.

        :params kwargs: any keyword arguments.
        """
        context: dict[str, list[dict | str]] = await self.get_common_context(
            **await super().get_context_data(**kwargs)
        )
        if isinstance(context, HttpResponseServerError):
            return context

        region = context["region"]
        cart: dict = await session_data.get_or_create_cart(self.request.session)
        region_products, subcategories_list = await asyncio.gather(
            crm_data.get_region_products(
                region["slug"],
                currency=context["selected_currency"],
                cart_ids_set={product["id"] for product in cart["products"]},
            ),
            crm_data.get_subcategories_list(),
        )

        context["quick_selection_subcategories"] = [
            subcategory
            for subcategory in subcategories_list
            if subcategory["slug"]
            in [product["subcategory_slug"] for product in region_products]
        ]

        context["region_bestsellers"] = utilities.get_region_bestsellers(region_products)

        cart_products = await common_handlers.get_cart_products(
            region["slug"], cart, context["selected_currency"]
        )
        context["additional_products"] = (
            await common_handlers.get_first_three_additional_products(
                region["slug"], region_products, cart_products
            )
        )
        seo_blocks = await self.get_seo_blocks()
        context["first_seo_block"] = seo_blocks[0]
        context["second_seo_block"] = seo_blocks[1]
        if not context["first_seo_block"].picture or not context["second_seo_block"].picture:
            return HttpResponseServerError(
                render(
                    self.request,
                    "templates/notification.html",
                    {
                        "header": "Server error",
                        "message_top": "We are so sorry, but the shop isn't \
                            initialized properly (seo-blocks)",
                        "message_bottom": "You can notify an owner about it",
                        "redirect_link": ".",
                        "redirect_message": "Repeat again",
                    },
                ),
                status=503,
            )

        main_slider = await self.get_main_slider()
        context["main_slider"] = main_slider
        return context

    @sync_to_async
    def get_seo_blocks(self):
        """To return SEO-block asynchronously."""
        return list(SeoBlock.objects.all()[:2])

    @sync_to_async
    def get_main_slider(self):
        """To return main slider asynchronously."""
        return list(MainSlider.objects.all())

    async def get(self, request, *args, **kwargs):
        """Asynchronous variation of GET method."""
        context = await self.get_context_data(**kwargs)
        if isinstance(context, HttpResponseServerError):
            return context
        return self.render_to_response(context)
