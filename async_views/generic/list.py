"""Module for Django async list CBV and mixins."""
from typing import Any, Dict, List, Optional, Tuple, Union

from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import InvalidPage, Paginator
from django.db import models
from django.db.models import QuerySet
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.list import MultipleObjectTemplateResponseMixin

from async_views.generic.base import AsyncContextMixin


class AsyncMultipleObjectMixin(AsyncContextMixin):
    """
    MultipleObjectMixin async_views analog.

    A mixin for views manipulating multiple objects.
    """

    allow_empty: bool = True
    context_object_name: Optional[str] = None
    model: Optional[models.Model] = None
    ordering: Optional[Union[List, str, Tuple]] = None
    page_kwarg: str = "page"
    paginate_by: Optional[int] = None
    paginate_orphans: int = 0
    paginator_class: Paginator = Paginator
    queryset: Optional[QuerySet] = None

    async def get_allow_empty(self):
        """
        Return ``True`` if the view should display empty lists.

        And ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    async def get_context_data(
        self, *, object_list: Optional[Union[List, QuerySet]] = None, **kwargs: Any
    ) -> Dict:
        """Get the context for this view."""
        queryset: Union[List, QuerySet] = (
            object_list if object_list is not None else self.object_list
        )
        bool(queryset)
        page_size = await self.get_paginate_by(queryset)
        context_object_name = await self.get_context_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = await self.paginate_queryset(
                queryset, page_size
            )
            context = {
                "paginator": paginator,
                "page_obj": page,
                "is_paginated": is_paginated,
                "object_list": queryset,
            }
        else:
            context = {
                "paginator": None,
                "page_obj": None,
                "is_paginated": False,
                "object_list": queryset,
            }
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        return await super().get_context_data(**context)

    async def get_context_object_name(
        self, object_list: Optional[Union[List, QuerySet]]
    ) -> Optional[str]:
        """Get the name of the item to be used in the context."""
        if self.context_object_name:
            return self.context_object_name
        elif hasattr(object_list, "model"):
            return "%s_list" % object_list.model._meta.model_name
        else:
            return None

    async def get_ordering(self) -> Optional[Union[List, str]]:
        """Return the field or fields to use for ordering the queryset."""
        return self.ordering

    async def get_paginate_by(self, queryset: QuerySet) -> Optional[int]:
        """Get the number of items to paginate by, or ``None`` for no pagination."""
        return self.paginate_by

    async def get_paginate_orphans(self) -> int:
        """
        Get_paginate_orphans async_views analog.

        Return the maximum number of orphans extend the last page
        by when paginating.
        """
        return self.paginate_orphans

    async def get_paginator(
        self,
        queryset: QuerySet,
        per_page: int,
        orphans: int = 0,
        allow_empty_first_page: bool = True,
        **kwargs: Any,
    ):
        """Return an instance of the paginator for this view."""
        return self.paginator_class(
            queryset,
            per_page,
            orphans=orphans,
            allow_empty_first_page=allow_empty_first_page,
            **kwargs,
        )

    async def get_queryset(self) -> QuerySet:
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.queryset is not None:
            queryset: QuerySet = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

    async def paginate_queryset(self, queryset: QuerySet, page_size: int) -> Optional[Tuple]:
        """Paginate the queryset, if needed."""
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=await self.get_paginate_orphans(),
            allow_empty_first_page=await self.get_allow_empty(),
        )
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == "last":
                page_number = paginator.num_pages
            else:
                raise Http404(_("Page is not “last”, nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return paginator, page, page.object_list, page.has_other_pages()
        except InvalidPage as e:
            raise Http404(
                _("Invalid page (%(page_number)s): %(message)s")
                % {"page_number": page_number, "message": str(e)}
            )


class AsyncBaseListView(AsyncMultipleObjectMixin, View):
    """
    BaseListView async_views analog.

    A base view for displaying a list of objects.
    """


class AsyncListView(MultipleObjectTemplateResponseMixin, AsyncBaseListView):
    """
    ListView async_views analog.

    Render some list of objects, set by `self.model` or `self.queryset`.
    `self.queryset` can actually be any iterable of items, not just a queryset.
    """
