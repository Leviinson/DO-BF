from typing import Any

from asgiref.sync import sync_to_async
from django.http import HttpResponse, HttpResponseServerError

from async_views.generic.base import AsyncTemplateView
from services.mixins import ApplicationMixin

from .models import AboutUsContextModel, ContactsDataModel, DeliveryDataModel


# Create your views here.
class AboutUsView(AsyncTemplateView, ApplicationMixin):
    """Class view for process adding product to customer ordered products."""

    http_method_names = ["get"]
    template_name = "fillers/about.html"

    async def get(self, request, *args, **kwargs) -> HttpResponse:
        """Asynchronous variation of GET method."""
        context = await self.get_context_data(**kwargs)
        if isinstance(context, HttpResponseServerError):
            return context
        response = self.render_to_response(context)
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
        context["about_us_context"] = (await self.get_about_us_context())[0]
        if isinstance(context, HttpResponseServerError):
            return context
        return context

    @sync_to_async
    def get_about_us_context(self):
        """To return 'about us' context asynchronously from DB."""
        return list(AboutUsContextModel.objects.all()[:1])


class DeliveryView(AsyncTemplateView, ApplicationMixin):
    """Class view for process adding product to customer ordered products."""

    http_method_names = ["get"]
    template_name = "fillers/delivery.html"

    async def get(self, request, *args, **kwargs) -> HttpResponse:
        """Asynchronous variation of GET method."""
        context = await self.get_context_data(**kwargs)
        if isinstance(context, HttpResponseServerError):
            return context
        response = self.render_to_response(context)
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
        context["delivery_context"] = (await self.get_delivery_context())[0]
        if isinstance(context, HttpResponseServerError):
            return context
        return context

    @sync_to_async
    def get_delivery_context(self):
        """To return 'about us' context asynchronously from DB."""
        return list(DeliveryDataModel.objects.all()[:1])


class ContactsView(AsyncTemplateView, ApplicationMixin):
    """Class view for process adding product to customer ordered products."""

    http_method_names = ["get"]
    template_name = "fillers/contacts.html"

    async def get(self, request, *args, **kwargs) -> HttpResponse:
        """Asynchronous variation of GET method."""
        context = await self.get_context_data(**kwargs)
        if isinstance(context, HttpResponseServerError):
            return context
        response = self.render_to_response(context)
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
        context["contacts_context"] = (await self.get_contacts_context())[0]
        if isinstance(context, HttpResponseServerError):
            return context
        return context

    @sync_to_async
    def get_contacts_context(self):
        """To return 'about us' context asynchronously from DB."""
        return list(ContactsDataModel.objects.all()[:1])
