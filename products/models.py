"""Models for 'product' app."""

from typing import List

from asgiref.sync import sync_to_async
from django.db import models


class ZohoModuleRecord(models.Model):
    """Model for storing Zoho CRM module id storage."""

    id = models.BigIntegerField(
        primary_key=True,
        verbose_name="Id записи",
    )
    module_name = models.CharField(
        max_length=100,
        verbose_name="Наименование модуля",
    )
    record_name = models.CharField(
        max_length=100,
        verbose_name="Наименование записи",
    )
    accessed_at = models.DateField(
        auto_now=True,
        verbose_name="Последняя дата доступа",
    )

    def __str__(self) -> str:
        """Represent class instance."""
        return f"{self.module_name} {self.record_name}"


class ZohoImage(models.Model):
    """Model for storing Zoho CRM images."""

    id = models.BigIntegerField(
        primary_key=True,
        verbose_name="Id картинки",
    )
    zoho_record = models.ForeignKey(
        ZohoModuleRecord,
        on_delete=models.CASCADE,
        verbose_name="Зохо запись",
    )
    image = models.ImageField(verbose_name="Адресс картинки")

    @classmethod
    @sync_to_async
    def avalues_list(cls, *args, **kwargs) -> List:
        """
        Async implementation of "filter" method.

        Is async because of this one exception:
        django.core.exceptions.SynchronousOnlyOperation:
        You cannot call this from an async context - use a thread or sync_to_async.
        """
        return list(cls.objects.filter(*args, **kwargs))

    def __str__(self) -> str:
        """Represent class instance."""
        return f"{self.image}"
