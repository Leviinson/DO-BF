"""Module for forms with async_views functionality for 'API' project."""
from itertools import chain
from typing import Dict, List, Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet
from django.forms import model_to_dict
from django.forms.forms import BaseForm, DeclarativeFieldsMetaclass
from django.forms.models import ModelFormMetaclass
from django.forms.utils import ErrorDict, ErrorList


def get_unique_fields(model: models.Model, fields: List, exclude: List) -> List:
    """Get unique model fields list."""
    opts = model._meta
    unique_fields = []
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, "editable", False):
            continue
        if fields is not None and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if f.unique:
            unique_fields.append(f.name)
    return unique_fields


class AsyncBaseForm(BaseForm):
    """
    Custom Django form with async_views functionality.

    To standart Form functionality added async_is_valid method, that trigger
    form cleaned data creation and using async_errors -> async_full_clean ->
    sync clean_fields -> _async_clean_form -> async_clean -> _async_post_clean.
    Using async_is_valid we can run form validation is async_views functions.
    """

    async def async_is_valid(self) -> bool:
        """Return True if the form has no errors, or False otherwise. Async variant."""
        return self.is_bound and not await self.async_errors

    @property
    async def async_errors(self):
        """Return an ErrorDict for the data provided for the form. Async variant."""
        if self._errors is None:
            await self.async_full_clean()
        return self._errors

    async def async_full_clean(self) -> None:
        """
        Clean all of self.data and populate self._errors and self.cleaned_data.

        Async variant.
        """
        self._errors: ErrorDict = ErrorDict()
        if not self.is_bound:
            return
        self.cleaned_data: Dict = {}
        if self.empty_permitted and not self.has_changed():
            return
        self._clean_fields()
        await self._async_clean_form()
        await self._async_post_clean()

    async def _async_clean_form(self) -> None:
        """Clean form data. Async variant."""
        try:
            cleaned_data: Dict = await self.async_clean()
        except ValidationError as e:
            self.add_error(None, e)
        else:
            if cleaned_data is not None:
                self.cleaned_data = cleaned_data

    async def async_clean(self) -> Optional[Dict]:
        """
        Clean data. Async variant.

        Hook for doing any extra form-wide cleaning after Field.clean() has been
        called on every field. Any ValidationError raised by this method will
        not be associated with a particular field; it will have a special-case
        association with the field named '__all__'.

        """
        return self.cleaned_data

    async def _async_post_clean(self) -> None:
        """
        Perform post clean. Async variant.

        An internal hook for performing additional cleaning after form cleaning
        is complete. Used for model validation in model forms.
        """
        pass


class AsyncForm(AsyncBaseForm, metaclass=DeclarativeFieldsMetaclass):
    """
    A collection of Fields, plus their associated data.

    With async_views functionality.
    """

    # This is a separate class from BaseForm in order to abstract the way
    # self.fields is specified. This class (Form) is the one that does the
    # fancy metaclass stuff purely for the semantic sugar -- it allows one
    # to define a form using declarative syntax.
    # BaseForm itself has no way of designating self.fields.


class AsyncBaseModelForm(AsyncBaseForm):
    """
    Custom Django form for unique check with async_views functionality.

    Class based on AsyncForm functionality (with added async_is_valid),
    new form class must be defined similar to Meta model, fields, exclude
    definition. Custom instance attributes added:
    self.unique_fields - models fields names list, which has unique=True and
    are in accordance with Meta fields and exclude attrs;
    self.model_pk - model instance pk, if instance is not None.
    This class hos not all functionality comparing to its sync variant.
    Class instance has it's own 'save' method - async_save, which uses
    'aupdate' and 'acreate' functionality.
    """

    def __init__(
        self,
        data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        instance=None,
        field_order=None,
        use_required_attribute=None,
        renderer=None,
    ):
        """
        Initialize custom Django model form with async_views functionality.

        Additional to AsyncForm attributes:
        self.unique_fields - model fields names list, that has unique=True;
        self.model_pk - instance pk, if instance is not None.
        """
        self.model_pk: int = None
        opts = self._meta
        if opts.model is None:
            raise ValueError("ModelForm has no model class specified.")
        if instance is None:
            # if we didn't get an instance, instantiate a new one
            self.instance = opts.model()
            object_data: Dict = {}
        else:
            self.model_pk = instance.pk
            self.instance = instance
            object_data = model_to_dict(instance, opts.fields, opts.exclude)
        self.unique_fields: List = get_unique_fields(opts.model, opts.fields, opts.exclude)
        # if initial was provided, it should override the values from instance
        if initial is not None:
            object_data.update(initial)
        # self._validate_unique will be set to True by BaseModelForm.clean().
        # It is False by default so overriding self.clean() and failing to call
        # super will stop validate_unique from being called.
        super().__init__(
            data,
            files,
            auto_id,
            prefix,
            object_data,
            error_class,
            label_suffix,
            empty_permitted,
            field_order,
            use_required_attribute,
            renderer,
        )

    async def async_validate_unique(self, unique_fields: List) -> None:
        """Validate unique model fields. Async variant."""
        queryset: QuerySet = self._meta.model.objects.all()
        if self.model_pk:
            queryset = queryset.exclude(pk=self.model_pk)
        for field in unique_fields:
            if value := self.cleaned_data.get(field):
                field_dict: Dict = {field: value}
                if await queryset.filter(**field_dict).aexists():
                    self.add_error(
                        field,
                        ValidationError(
                            {field: f"{field} {value} already exists. Try another one."}
                        ),
                    )
            else:
                self.add_error(
                    field, ValidationError({field: f"Field {field} must not be empty."})
                )

    async def async_save(self) -> None:
        """Save models instance with async_views functionality."""
        if self.model_pk:
            await self._meta.model.objects.filter(pk=self.model_pk).aupdate(**self.cleaned_data)
        else:
            await self._meta.model.objects.acreate(**self.cleaned_data)

    async def _async_post_clean(self) -> None:
        """Perform post clean. Async variant."""
        if self.unique_fields:
            await self.async_validate_unique(self.unique_fields)


class AsyncModelForm(AsyncBaseModelForm, metaclass=ModelFormMetaclass):
    """Custom model form with async_views functionality."""
