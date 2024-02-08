"""Mixins class for 'userprofile' app."""
from abc import ABC
from typing import Any, Dict

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.urls import reverse_lazy
from django.views.generic import FormView

from async_views.auth.mixins import AsyncUserPassesTestMixin
from async_views.generic.base import AsyncTemplateView
from async_views.generic.edit import AsyncFormView
from services.mixins import ApplicationMixin


class UserProfileTemplateView(
    ApplicationMixin, AsyncUserPassesTestMixin, AsyncTemplateView, ABC
):
    """Custom TemplateView for using in 'userprofile' app."""

    async def get(self, request, *args, **kwargs):
        """
        Async implementation of the method.

        It uses async implementation of ApplicationMixin.
        """
        context = await self.get_context_data(**kwargs)
        if isinstance(context, HttpResponseServerError):
            return context
        return self.render_to_response(context)

    async def test_func(self, **kwargs: Any) -> bool:
        """Test whether kwargs pk is equal user.zoho_id."""
        user = await sync_to_async(get_user)(self.request)
        if user.is_anonymous:
            return False
        return user.zoho_id == self.kwargs.get("pk")


class UserProfileFormView(ApplicationMixin, UserPassesTestMixin, FormView, ABC):
    """Custom FormView for using in 'userprofile' app."""

    async def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Async implementation of the method.

        It uses async implementation of ApplicationMixin.
        """
        return await self.get_common_context(**super().get_context_data(**kwargs))

    async def get(self, request, *args, **kwargs):
        """Handle GET requests: instantiate a blank version of the form."""
        context = await self.get_context_data(*args, **kwargs)
        if isinstance(context, HttpResponseServerError):
            return context
        return self.render_to_response(context)

    async def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """
        Is async because of the django.core.exceptions.ImproperlyConfigured exception.

        /"subclass name"/ HTTP handlers must either be all sync or all async.
        """
        return super().post(request, *args, **kwargs)

    async def put(self, *args: str, **kwargs: Any) -> HttpResponse:
        """
        Is async because of the django.core.exceptions.ImproperlyConfigured exception.

        /"subclass name"/ HTTP handlers must either be all sync or all async.
        """
        return super().put(*args, **kwargs)

    def test_func(self, **kwargs: Any) -> bool:
        """Test whether kwargs pk is equal user.zoho_id."""
        if self.request.user.is_anonymous:
            return False
        return self.request.user.zoho_id == self.kwargs.get("pk")

    def get_success_url(self) -> HttpResponseRedirect:
        """Get success url for redirect."""
        url = super().get_success_url()
        return reverse_lazy(url, kwargs={"pk": self.request.user.zoho_id})


class AsyncUserProfileFormView(ApplicationMixin, AsyncUserPassesTestMixin, AsyncFormView):
    """Custom async_views FormView for using in 'userprofile' app."""

    async def test_func(self, **kwargs: Any) -> bool:
        """Test whether kwargs pk is equal user.zoho_id."""
        user = await self.get_user_from_request(self.request)
        if user.is_anonymous:
            return False
        return self.request.user.zoho_id == self.kwargs.get("pk")

    async def get_success_url(self) -> HttpResponseRedirect:
        """Get success url for redirect."""
        url = await super().get_success_url()
        return reverse_lazy(url, kwargs={"pk": self.request.user.zoho_id})
