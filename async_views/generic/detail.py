"""Module for Django async detail CBV and mixins."""
from typing import Any, Dict, Optional

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.detail import SingleObjectTemplateResponseMixin

from async_views.generic.base import AsyncContextMixin


class AsyncSingleObjectMixin(AsyncContextMixin):
    """
    SingleObjectMixin async_views variant.

    Provide the ability to retrieve a single object for further manipulation.
    """

    context_object_name: Optional[str] = None
    model: Optional[models.Model] = None
    pk_url_kwarg: str = "pk"
    query_pk_and_slug: bool = False
    queryset: Optional[QuerySet] = None
    slug_field: str = "slug"
    slug_url_kwarg: str = "slug"

    async def get_context_data(self, **kwargs: Any) -> Dict:
        """Insert the single object into the context dict."""
        context = {}
        if self.object:
            context["object"] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context.update(kwargs)
        return await super().get_context_data(**context)

    async def get_context_object_name(self, obj: models.Model) -> Optional[str]:
        """Get the name to use for the object."""
        if self.context_object_name:
            return self.context_object_name
        if isinstance(obj, models.Model):
            return obj._meta.model_name
        return None

    async def get_object(self, queryset: Optional[QuerySet] = None) -> models.Model:
        """
        Return the object the view is displaying. Async functionality.

        Require `self.queryset` and a `pk` or `slug` argument in the URLconf.
        Subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = await self.get_queryset()
        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)
        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = await self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})
        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )
        try:
            # Get the single item from the filtered queryset
            obj = await queryset.aget()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj

    async def get_queryset(self) -> QuerySet:
        """
        Return the `QuerySet` that will be used to look up the object.

        This method is called by the default implementation of get_object() and
        may not be called if get_object() is overridden.
        """
        if self.queryset is None:
            if self.model:
                return self.model._default_manager.all()
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.model, %(cls)s.queryset, or override "
                    "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
                )
        return self.queryset.all()

    async def get_slug_field(self) -> str:
        """Get the name of a slug field to be used to look up by slug."""
        return self.slug_field


class AsyncBaseDetailView(AsyncSingleObjectMixin, View):
    """
    BaseDetailView async_views analog.

    A base view for displaying a single object.
    """

    async def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Modify get method - instantiate self.object, if it exists.

        Handle GET requests: instantiate a blank version of the form.
        """
        self.object = await self.get_object()
        context = await self.get_context_data(object=self.object)
        return self.render_to_response(context)


class AsyncDetailView(SingleObjectTemplateResponseMixin, AsyncBaseDetailView):
    """
    DetailView async_views analog.

    Render a "detail" view of an object.
    By default this is a model instance looked up from `self.queryset`, but the
    view will support display of *any* object by overriding `self.get_object()`.
    """
