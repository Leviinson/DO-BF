"""Module for Django async detail CBV and mixins."""
from datetime import datetime
from typing import Any, List, Optional, Tuple

from django.db import models
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.dates import (
    DateMixin,
    DayMixin,
    MonthMixin,
    WeekMixin,
    YearMixin,
    _date_from_string,
    timezone_today,
)
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.list import MultipleObjectTemplateResponseMixin

from async_views.generic.detail import AsyncBaseDetailView
from async_views.generic.list import AsyncMultipleObjectMixin


class AsyncBaseDateDetailView(YearMixin, MonthMixin, DayMixin, DateMixin, AsyncBaseDetailView):
    """BaseDateDetailView async_views analog."""

    async def get_object(self, queryset: QuerySet = None) -> models.Model:
        """Get the object this request displays."""
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        date = _date_from_string(
            year,
            self.get_year_format(),
            month,
            self.get_month_format(),
            day,
            self.get_day_format(),
        )
        # Use a custom queryset if provided
        qs = self.get_queryset() if queryset is None else queryset
        if not self.get_allow_future() and date > datetime.date.today():
            raise Http404(
                _(
                    "Future %(verbose_name_plural)s not available because "
                    "%(class_name)s.allow_future is False."
                )
                % {
                    "verbose_name_plural": qs.model._meta.verbose_name_plural,
                    "class_name": self.__class__.__name__,
                }
            )
        # Filter down a queryset from self.queryset using the date from the
        # URL. This'll get passed as the queryset to DetailView.get_object,
        # which'll handle the 404
        lookup_kwargs = self._make_single_date_lookup(date)
        qs = qs.filter(**lookup_kwargs)
        return await super().get_object(queryset=qs)


class AsyncDateDetailView(SingleObjectTemplateResponseMixin, AsyncBaseDateDetailView):
    """DateDetailView async_views analog."""


class AsyncBaseDateListView(AsyncMultipleObjectMixin, DateMixin, View):
    """
    BaseDateListView async_views analog.

    Abstract base class for date-based views displaying a list of objects.
    """

    allow_empty: bool = False
    date_list_period: str = "year"

    async def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Handle async_views get request."""
        self.date_list, self.object_list, extra_context = await self.get_dated_items()
        context = await self.get_context_data(
            object_list=self.object_list, date_list=self.date_list, **extra_context
        )
        return self.render_to_response(context)

    async def get_date_list(
        self,
        queryset: QuerySet,
        date_type: Optional[str] = None,
        ordering: str = "ASC",
    ) -> Optional[List]:
        """
        get_date_list async_views analog.

        Get a date list by calling `queryset.dates/datetimes()`, checking
        along the way for empty lists that aren't allowed.
        """
        date_field = self.get_date_field()
        allow_empty = self.get_allow_empty()
        if date_type is None:
            date_type = await self.get_date_list_period()
        if self.uses_datetime_field:
            date_list = queryset.datetimes(date_field, date_type, ordering)
        else:
            date_list = queryset.dates(date_field, date_type, ordering)
        if date_list is not None and not date_list and not allow_empty:
            raise Http404(
                _("No %(verbose_name_plural)s available")
                % {
                    "verbose_name_plural": queryset.model._meta.verbose_name_plural,
                }
            )
        return date_list

    async def get_date_list_period(self) -> str:
        """
        Get the aggregation period for the list of dates.

        'year', 'month' or 'day'.
        """
        return self.date_list_period

    async def get_dated_items(self) -> None:
        """Obtain the list of dates and items."""
        raise NotImplementedError(
            "A DateView must provide an implementation of get_dated_items()"
        )

    async def get_dated_queryset(self, **lookup: Any) -> QuerySet:
        """
        get_dated_queryset async_views analog.

        Get a queryset properly filtered according to `allow_future` and any
        extra lookup kwargs.
        """
        qs = self.get_queryset().filter(**lookup)
        date_field = self.get_date_field()
        allow_future = self.get_allow_future()
        allow_empty = self.get_allow_empty()
        paginate_by = self.get_paginate_by(qs)
        if not allow_future:
            now = timezone.now() if self.uses_datetime_field else timezone_today()
            qs = qs.filter(**{"%s__lte" % date_field: now})
        if not allow_empty:
            # When pagination is enabled, it's better to do a cheap query
            # than to load the unpaginated queryset in memory.
            is_empty = not qs if paginate_by is None else not qs.exists()
            if is_empty:
                raise Http404(
                    _("No %(verbose_name_plural)s available")
                    % {
                        "verbose_name_plural": qs.model._meta.verbose_name_plural,
                    }
                )
        bool(qs)
        return qs

    def get_ordering(self):
        """
        Return the field or fields to use for ordering the queryset.

        Use the date field by default.
        """
        return "-%s" % self.get_date_field() if self.ordering is None else self.ordering


class AsyncBaseDayArchiveView(YearMixin, MonthMixin, DayMixin, AsyncBaseDateListView):
    """
    BaseDayArchiveView async_views analog.

    List of objects published on a given day.
    """

    async def _get_dated_items(self, date: str) -> Tuple:
        """
        _get_dated_items async_views analog.

        Do the actual heavy lifting of getting the dated items; this accepts a
        date object so that TodayArchiveView can be trivial.
        """
        lookup_kwargs = self._make_single_date_lookup(date)
        qs = await self.get_dated_queryset(**lookup_kwargs)
        return (
            None,
            qs,
            {
                "day": date,
                "previous_day": self.get_previous_day(date),
                "next_day": self.get_next_day(date),
                "previous_month": self.get_previous_month(date),
                "next_month": self.get_next_month(date),
            },
        )

    async def get_dated_items(self) -> Tuple:
        """Return (date_list, items, extra_context) for this request."""
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        date = _date_from_string(
            year,
            self.get_year_format(),
            month,
            self.get_month_format(),
            day,
            self.get_day_format(),
        )
        return await self._get_dated_items(date)


class AsyncBaseMonthArchiveView(YearMixin, MonthMixin, AsyncBaseDateListView):
    """
    BaseMonthArchiveView async_views analog.

    List of objects published in a given month.
    """

    date_list_period: str = "day"

    async def get_dated_items(self) -> Tuple:
        """Return (date_list, items, extra_context) for this request."""
        year = self.get_year()
        month = self.get_month()
        date_field = self.get_date_field()
        date = _date_from_string(year, self.get_year_format(), month, self.get_month_format())
        since = self._make_date_lookup_arg(date)
        until = self._make_date_lookup_arg(self._get_next_month(date))
        lookup_kwargs = {
            "%s__gte" % date_field: since,
            "%s__lt" % date_field: until,
        }
        qs = await self.get_dated_queryset(**lookup_kwargs)
        date_list = self.get_date_list(qs)
        return (
            date_list,
            qs,
            {
                "month": date,
                "next_month": self.get_next_month(date),
                "previous_month": self.get_previous_month(date),
            },
        )


class AsyncBaseTodayArchiveView(AsyncBaseDayArchiveView):
    """
    BaseTodayArchiveView async_views analog.

    List of objects published today.
    """

    async def get_dated_items(self) -> Tuple:
        """Return (date_list, items, extra_context) for this request."""
        return await self._get_dated_items(datetime.date.today())


class AsyncBaseWeekArchiveView(YearMixin, WeekMixin, AsyncBaseDateListView):
    """
    BaseWeekendArchiveView async_views analog.

    List of objects published in a given week.
    """

    async def get_dated_items(self) -> Tuple:
        """Return (date_list, items, extra_context) for this request."""
        year = self.get_year()
        week = self.get_week()
        date_field = self.get_date_field()
        week_format = self.get_week_format()
        week_choices = {"%W": "1", "%U": "0", "%V": "1"}
        try:
            week_start = week_choices[week_format]
        except KeyError:
            raise ValueError(
                "Unknown week format %r. Choices are: %s"
                % (
                    week_format,
                    ", ".join(sorted(week_choices)),
                )
            )
        year_format = self.get_year_format()
        if week_format == "%V" and year_format != "%G":
            raise ValueError(
                "ISO week directive '%s' is incompatible with the year "
                "directive '%s'. Use the ISO year '%%G' instead."
                % (
                    week_format,
                    year_format,
                )
            )
        date = _date_from_string(year, year_format, week_start, "%w", week, week_format)
        since = self._make_date_lookup_arg(date)
        until = self._make_date_lookup_arg(self._get_next_week(date))
        lookup_kwargs = {
            "%s__gte" % date_field: since,
            "%s__lt" % date_field: until,
        }
        qs = self.get_dated_queryset(**lookup_kwargs)
        return (
            None,
            qs,
            {
                "week": date,
                "next_week": self.get_next_week(date),
                "previous_week": self.get_previous_week(date),
            },
        )


class AsyncBaseYearArchiveView(YearMixin, AsyncBaseDateListView):
    """BaseYearArchiveView async_views analog."""

    date_list_period: str = "month"
    make_object_list: bool = False

    async def get_dated_items(self) -> Tuple:
        """Return (date_list, items, extra_context) for this request."""
        year = self.get_year()
        date_field = self.get_date_field()
        date = _date_from_string(year, self.get_year_format())
        since = self._make_date_lookup_arg(date)
        until = self._make_date_lookup_arg(self._get_next_year(date))
        lookup_kwargs = {
            "%s__gte" % date_field: since,
            "%s__lt" % date_field: until,
        }
        qs = self.get_dated_queryset(**lookup_kwargs)
        date_list = self.get_date_list(qs)
        if not await self.get_make_object_list():
            # We need this to be a queryset since parent classes introspect it
            # to find information about the model.
            qs = qs.none()
        return (
            date_list,
            qs,
            {
                "year": date,
                "next_year": self.get_next_year(date),
                "previous_year": self.get_previous_year(date),
            },
        )


class AsyncDayArchiveView(MultipleObjectTemplateResponseMixin, AsyncBaseDayArchiveView):
    """
    DayArchiveView async_views analog.

    List of objects published on a given day.
    """

    template_name_suffix: str = "_archive_day"


class AsyncMonthArchiveView(MultipleObjectTemplateResponseMixin, AsyncBaseMonthArchiveView):
    """
    MonthArchiveView async_views analog.

    List of objects published in a given month.
    """

    template_name_suffix: str = "_archive_month"


class AsyncTodayArchiveView(MultipleObjectTemplateResponseMixin, AsyncBaseTodayArchiveView):
    """
    TodayArchiveView async_views analog.

    List of objects published today.
    """

    template_name_suffix: str = "_archive_day"


class AsyncWeekArchiveView(MultipleObjectTemplateResponseMixin, AsyncBaseWeekArchiveView):
    """
    WeekArchiveView async_views analog.

    List of objects published in a given week.
    """

    template_name_suffix: str = "_archive_week"


class AsyncYearArchiveView(MultipleObjectTemplateResponseMixin, AsyncBaseYearArchiveView):
    """
    YearArchiveView async_views analog.

    List of objects published in a given year.
    """

    template_name_suffix: str = "_archive_year"


class AsyncBaseArchiveIndex(AsyncBaseDateListView):
    """
    BaseArchiveIndex async analog.

    Base class for archives of date-based items. Requires a response mixin.
    """

    context_object_name: str = "latest"

    async def get_dated_items(self) -> Tuple:
        """Return (date_list, items, extra_context) for this request."""
        qs = await self.get_dated_queryset()
        date_list = await self.get_date_list(qs, ordering="DESC")
        if not date_list:
            qs = qs.none()
        return date_list, qs, {}


class AsyncArchiveIndexView(MultipleObjectTemplateResponseMixin, AsyncBaseArchiveIndex):
    """
    ArchiveIndexView async analog.

    Top-level archive of date-based items.
    """

    template_name_suffix: str = "_archive"
