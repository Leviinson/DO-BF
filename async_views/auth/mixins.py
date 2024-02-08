"""Mixins for async auth views."""
from typing import Any, List, Optional, Union
from urllib.parse import urlparse

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import Permission
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import resolve_url


class AsyncAccessMixin:
    """
    AccessMixin async analog.

    Abstract CBV mixin that gives access mixins the same customizable
    functionality.
    """

    login_url: Optional[str] = None
    permission_denied_message: str = ""
    raise_exception: bool = False
    redirect_field_name: str = "next"

    async def get_login_url(self) -> str:
        """Override this method to override the login_url attribute."""
        login_url = self.login_url or settings.LOGIN_URL
        if not login_url:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing the login_url attribute. "
                f"Define {self.__class__.__name__}.login_url, settings.LOGIN_URL, "
                f"or override {self.__class__.__name__}.get_login_url()."
            )
        return str(login_url)

    async def get_permission_denied_message(self) -> str:
        """Override this method to override the permission_denied_message attribute."""
        return self.permission_denied_message

    async def get_redirect_field_name(self) -> str:
        """Override this method to override the redirect_field_name attribute."""
        return self.redirect_field_name

    async def handle_no_permission(self) -> HttpResponseRedirect:
        """Handle no permission."""
        user = await sync_to_async(auth.get_user)(self.request)
        if self.raise_exception or user.is_authenticated:
            raise PermissionDenied(await self.get_permission_denied_message())
        path = self.request.build_absolute_uri()
        resolved_login_url = resolve_url(await self.get_login_url())
        # If the login url is the same scheme and net location then use the
        # path as the "next" url.
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if (not login_scheme or login_scheme == current_scheme) and (
            not login_netloc or login_netloc == current_netloc
        ):
            path = self.request.get_full_path()
        return await sync_to_async(redirect_to_login, thread_sensitive=False)(
            path,
            resolved_login_url,
            await self.get_redirect_field_name(),
        )


class AsyncUserPassesTestMixin(AsyncAccessMixin):
    """
    UserPassesTestMixin async account.

    Deny a request with a permission error if the test_func() method returns
    False.
    """

    async def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Dispatch async analog. Rewrite dispatch."""
        user_test_result = await (await self.get_test_func())()
        if not user_test_result:
            return await self.handle_no_permission()
        return await super().dispatch(request, *args, **kwargs)

    async def get_test_func(self) -> Any:
        """Override this method to use a different test_func method."""
        return self.test_func

    async def test_func(self):
        """Implement test functionality."""
        raise NotImplementedError(
            "{} is missing the implementation of the test_func() method.".format(
                self.__class__.__name__
            )
        )


class AsyncLoginRequiredMixin(AsyncAccessMixin):
    """
    LoginRequiredMixin async analog.

    Verify that the current user is authenticated.
    """

    async def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Dispatch async analog. Rewrite dispatch."""
        user = await sync_to_async(auth.get_user, thread_sensitive=False)(request)
        if not user.is_authenticated:
            return await self.handle_no_permission()
        return await super().dispatch(request, *args, **kwargs)


class AsyncPermissionRequiredMixin(AsyncAccessMixin):
    """
    PermissionRequiredMixin async analog.

    Verify that the current user has all specified permissions.
    """

    permission_required: Union[str, List[Permission]] = None

    async def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Dispatch async analog. Rewrite dispatch."""
        if not await self.has_permission():
            return await self.handle_no_permission()
        return await super().dispatch(request, *args, **kwargs)

    async def get_permission_required(self) -> Union[str, List[Permission]]:
        """
        Override this method to override the permission_required attribute.

        Must return an iterable.
        """
        if self.permission_required is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing the "
                f"permission_required attribute. Define "
                f"{self.__class__.__name__}.permission_required, or override "
                f"{self.__class__.__name__}.get_permission_required()."
            )
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms

    async def has_permission(self) -> Union[str, List[Permission]]:
        """Override this method to customize the way permissions are checked."""
        perms = self.get_permission_required()
        return await sync_to_async(self.request.user.has_perms, thread_sensitive=False)(perms)
