"""Module for Django async generic base CBV and mixins."""
import logging
from typing import Any, Dict, Optional

from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.http import (
    HttpRequest,
    HttpResponseGone,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from custom_auth.models import User

logger = logging.getLogger("django.request")


class AsyncContextMixin:
    """
    ContextMixin async_views analog.

    A default context mixin that passes the keyword arguments received by
    get_context_data() as the template context.
    Also added 'Get user from request' async_views functionality.
    """

    extra_context: Optional[Dict] = None

    async def get_context_data(self, **kwargs: Any) -> Dict:
        """Get context data for the view. Async variant."""
        kwargs.setdefault("view", self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return kwargs

    @sync_to_async(thread_sensitive=False)
    def get_user_from_request(self, request: HttpRequest) -> User | AnonymousUser | None:
        """Get request user inside async_views function."""
        return request.user if bool(request.user) else None


class AsyncRedirectView(View):
    """
    RedirectView async_views analog.

    Provide a redirect on any GET request.
    """

    pattern_name: Optional[str] = None
    permanent: bool = False
    query_string: bool = False
    url: Optional[str] = None

    async def delete(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect | HttpResponseGone | HttpResponsePermanentRedirect:
        """Call get method."""
        return await self.get(request, *args, **kwargs)

    async def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect | HttpResponseGone | HttpResponsePermanentRedirect:
        """Perform redirect."""
        url = await self.get_redirect_url(*args, **kwargs)
        if url:
            if self.permanent:
                return await sync_to_async(
                    HttpResponsePermanentRedirect, thread_sensitive=False
                )(url)
            else:
                return await sync_to_async(HttpResponseRedirect, thread_sensitive=False)(url)
        else:
            logger.warning(
                "Gone: %s", request.path, extra={"status_code": 410, "request": request}
            )
            return await sync_to_async(HttpResponseGone, thread_sensitive=False)()

    async def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """
        Return the URL redirect to.

        Keyword arguments from the URL pattern match generating the redirect request
        are provided as kwargs to this method.
        """
        if self.url:
            url = self.url % kwargs
        elif self.pattern_name:
            url = reverse(self.pattern_name, args=args, kwargs=kwargs)
        else:
            return None
        args = self.request.META.get("QUERY_STRING", "")
        if args and self.query_string:
            url = "%s?%s" % (url, args)
        return url

    async def head(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect | HttpResponseGone | HttpResponsePermanentRedirect:
        """Handle 'HEAD' request."""
        return await self.get(request, *args, **kwargs)

    async def options(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect | HttpResponseGone | HttpResponsePermanentRedirect:
        """Handle 'OPTIONS' request."""
        return await self.get(request, *args, **kwargs)

    async def patch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect | HttpResponseGone | HttpResponsePermanentRedirect:
        """Handle 'PATCH' request."""
        return await self.get(request, *args, **kwargs)

    async def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect | HttpResponseGone | HttpResponsePermanentRedirect:
        """Handle 'POST' request."""
        return await self.get(request, *args, **kwargs)

    async def put(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect | HttpResponseGone | HttpResponsePermanentRedirect:
        """Handle 'PUT' request."""
        return await self.get(request, *args, **kwargs)


class AsyncTemplateView(TemplateResponseMixin, AsyncContextMixin, View):
    """
    TemplateView async_views analog.

    Render a template. Pass keyword arguments from the URLconf to the context.
    """

    async def get(self, request, *args, **kwargs):
        """Async implementation of 'get' method."""
        context = await self.get_context_data(**kwargs)
        if isinstance(context, HttpResponseServerError):
            return context
        return self.render_to_response(context)
