"""Module for Django async edit CBV and mixins."""
import warnings
from typing import Any, Dict, List, Optional, Union

from django.core.exceptions import ImproperlyConfigured
from django.forms import modelform_factory
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.template.response import TemplateResponse
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import DeleteViewCustomDeleteWarning

from async_forms.async_forms import AsyncBaseForm, AsyncForm, AsyncModelForm
from async_views.generic.base import AsyncContextMixin
from async_views.generic.detail import AsyncBaseDetailView, AsyncSingleObjectMixin


class AsyncFormMixin(AsyncContextMixin):
    """
    Analoog FormMixin, async_views variant.

    Provide a way to show and handle a form in a request.
    """

    form_class: Optional[Union[AsyncForm, AsyncModelForm]] = None
    initial: Dict = {}
    prefix: Optional[str] = None
    success_url: Optional[str] = None

    async def form_invalid(self, form: AsyncForm) -> TemplateResponse:
        """
        Perform actions in case form is invalid.

        If the form is invalid, render the invalid form.
        """
        data: Dict = await self.get_context_data(form=form)
        return self.render_to_response(data)

    async def form_valid(self, form: AsyncForm | AsyncModelForm) -> HttpResponseRedirect:
        """
        Perform actions in case form is valid.

        If the form is valid, redirect to the supplied URL.
        """
        return HttpResponseRedirect(await self.get_success_url())

    async def get_context_data(self, **kwargs: Any) -> Dict:
        """Get context data for the view."""
        if "form" not in kwargs:
            kwargs["form"] = await self.get_form()
        return await super().get_context_data(**kwargs)

    async def get_form(
        self, form_class: Optional[Union[AsyncForm, AsyncModelForm]] = None
    ) -> Union[AsyncForm, AsyncModelForm]:
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = await self.get_form_class()
        kwargs = await self.get_form_kwargs()
        return form_class(**kwargs)

    async def get_form_class(self) -> Union[AsyncForm, AsyncModelForm]:
        """Return the form class to use."""
        return self.form_class

    async def get_form_kwargs(self) -> Dict:
        """Return the keyword arguments for instantiating the form."""
        kwargs: Dict = {
            "initial": await self.get_initial(),
            "prefix": self.get_prefix(),
        }
        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return kwargs

    async def get_initial(self) -> Optional[Dict]:
        """Return the initial data to use for the form on this view."""
        return self.initial.copy()

    def get_prefix(self) -> Optional[str]:
        """Return the prefix to use for forms."""
        return self.prefix

    async def get_success_url(self) -> str:
        """Return the URL to redirect to after processing a valid form."""
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)  # success_url may be lazy


class AsyncModelFormMixin(AsyncFormMixin, AsyncSingleObjectMixin):
    """
    ModelFormMixin async_views analog.

    Provide a way to show and handle a ModelForm in a request.
    """

    fields: Optional[List[str]] = None

    async def form_valid(self, form: AsyncForm | AsyncModelForm) -> HttpResponseRedirect:
        """If the form is valid, save the associated model."""
        self.object = await form.async_save()  # TODO check for async_save() to return something
        return await super().form_valid(form)

    def get_form_class(self):
        """Return the form class to use in this view."""
        if self.fields is not None and self.form_class:
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )
        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif getattr(self, "object", None) is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model
            if self.fields is None:
                raise ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )
            return modelform_factory(model, form=AsyncModelForm, fields=self.fields)

    async def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = await super().get_form_kwargs()
        if hasattr(self, "object"):
            kwargs.update({"instance": self.object})
        return kwargs

    async def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        if self.success_url:
            url = self.success_url.format(**self.object.__dict__)
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model."
                )
        return url


class AsyncProcessFormView(View):
    """
    ProcessFormView async_views analog.

    Render a form on GET and processes it on POST.
    """

    async def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Get method, async_views variant of CBV get method."""
        data: Dict = await self.get_context_data(**kwargs)
        if isinstance(data, HttpResponseServerError):
            return data
        return self.render_to_response(data)

    async def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Union[TemplateResponse, HttpResponseRedirect]:
        """
        Handle POST requests.

        Instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = await self.get_form()
        if await form.async_is_valid():
            return await self.form_valid(form)
        return await self.form_invalid(form)

    async def put(
        self, *args: Any, **kwargs: Any
    ) -> Union[TemplateResponse, HttpResponseRedirect]:
        """Handle PUT requests."""
        return await self.post(*args, **kwargs)


class AsyncBaseFormView(AsyncFormMixin, AsyncProcessFormView):
    """
    BaseFormView async_views analog.

    A base view for displaying a form.
    """


class AsyncFormView(TemplateResponseMixin, AsyncBaseFormView):
    """Custom async_views FormView analog."""


class AsyncBaseCreateView(AsyncModelFormMixin, AsyncProcessFormView):
    """
    BaseCreateView async_views analog.

    Base view for updating an existing object.
    """

    async def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Modify get method - instantiate self.object, if it exists.

        Handle GET requests: instantiate a blank version of the form.
        """
        self.object = None
        return await super().get(request, *args, **kwargs)

    async def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Union[TemplateResponse, HttpResponseRedirect]:
        """
        Rewrite post method, added self.object.

        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = None
        return await super().post(request, *args, **kwargs)


class AsyncCreateView(SingleObjectTemplateResponseMixin, AsyncBaseCreateView):
    """CreateView async_views analog."""

    template_name_suffix: str = "_form"


class AsyncDeletionMixin:
    """
    DeletionMixin async_views analog.

    Provide the ability to delete objects.
    """

    success_url: Optional[str] = None

    async def delete(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect:
        """
        Delete async_views analog.

        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = await self.get_object()
        success_url = await self.get_success_url()
        await self.object.__class__._default_manager.filter(pk=self.object.pk).adelete()
        return HttpResponseRedirect(success_url)

    async def get_success_url(self):
        """Get success url. Async variant."""
        if self.success_url:
            return self.success_url.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")

    async def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect:
        """Redirect to delete method."""
        return await self.delete(request, *args, **kwargs)


class AsyncBaseDeleteView(AsyncDeletionMixin, AsyncFormMixin, AsyncBaseDetailView):
    """
    BaseDeleteView async_views analog.

    Base view for deleting an object.
    Using this base class requires subclassing to provide a response mixin.
    """

    form_class: AsyncBaseForm = AsyncForm

    def __init__(self, *args, **kwargs):
        """
        Initialize self.

        See help(type(self)) for accurate signature.
        RemovedInDjango50Warning.
        """
        if self.__class__.delete is not AsyncDeletionMixin.delete:
            warnings.warn(
                f"DeleteView uses FormMixin to handle POST requests. As a "
                f"consequence, any custom deletion logic in "
                f"{self.__class__.__name__}.delete() handler should be moved "
                f"to form_valid().",
                DeleteViewCustomDeleteWarning,
                stacklevel=2,
            )
        super().__init__(*args, **kwargs)

    async def form_valid(self, form: AsyncForm | AsyncModelForm) -> HttpResponseRedirect:
        """If the form is valid, redirect to the supplied URL."""
        success_url = await self.get_success_url()
        await self.object.__class__._default_manager.filter(pk=self.object.pk).adelete()
        return HttpResponseRedirect(success_url)

    async def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Union[TemplateResponse, HttpResponseRedirect]:
        """
        Set self.object before the usual form processing flow.

        Inlined because having DeletionMixin as the first base, for
        get_success_url(), makes leveraging super() with ProcessFormView
        overly complex.
        """
        self.object = await self.get_object()
        form = await self.get_form()
        if await form.async_is_valid():
            return await self.form_valid(form)
        return await self.form_invalid(form)


class AsyncDeleteView(SingleObjectTemplateResponseMixin, AsyncBaseDeleteView):
    """DeleteView async_views analog."""

    template_name_suffix: str = "_confirm_delete"


class AsyncBaseUpdateView(AsyncModelFormMixin, AsyncProcessFormView):
    """
    BaseUpdateView async_views analog.

    Base view for updating an existing object.
    """

    async def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Modify get method - instantiate self.object, if it exists.

        Handle GET requests: instantiate a blank version of the form.
        """
        self.object = await self.get_object()
        return await super().get(request, *args, **kwargs)

    async def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Union[TemplateResponse, HttpResponseRedirect]:
        """
        Rewrite post method, added self.object.

        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = await self.get_object()
        return await super().post(request, *args, **kwargs)


class AsyncUpdateView(SingleObjectTemplateResponseMixin, AsyncBaseUpdateView):
    """UpdateView async_views analog."""

    template_name_suffix: str = "_form"
