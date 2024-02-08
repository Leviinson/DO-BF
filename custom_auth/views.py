"""Class and function views for 'custom_auth' app."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

from asgiref.sync import sync_to_async
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.urls import reverse_lazy

from async_views.auth.forms import AsyncAuthenticationForm
from async_views.auth.views import AsyncLoginView
from async_views.generic.edit import AsyncFormView
from services.crm_interface import custom_record_operations
from services.mixins import ApplicationMixin

from .forms import CustomUserCreationForm
from .models import User


class RegisterUserView(ApplicationMixin, AsyncFormView):
    """Class view for user registration with Zoho database storing data."""

    form_class = CustomUserCreationForm
    template_name = "custom_auth/sign_up.html"
    extra_context = {"title": "Sign up"}
    success_url = reverse_lazy("custom_auth:signup")

    async def get_context_data(self, **kwargs: Any) -> dict:
        """Get context data for the view."""
        return await self.get_common_context(**await super().get_context_data(**kwargs))

    async def get(self, request, *args, **kwargs):
        """Handle GET requests: instantiate a blank version of the form."""
        context = await self.get_context_data(*args, **kwargs)
        if isinstance(context, HttpResponseServerError):
            return context
        return self.render_to_response()

    async def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """
        Is async because of the django.core.exceptions.ImproperlyConfigured: exception.

        RegisterUserView HTTP handlers must either be all sync or all async.
        """
        return await super().post(request, *args, **kwargs)

    async def put(self, *args: str, **kwargs: Any) -> HttpResponse:
        """
        Is async because of the django.core.exceptions.ImproperlyConfigured exception.

        RegisterUserView HTTP handlers must either be all sync or all async.
        """
        return super().put(*args, **kwargs)

    async def form_valid(self, form: CustomUserCreationForm) -> HttpResponseRedirect:
        """Create new user. Add received after creating customer in Zoho CRM zoho_id."""
        user: User = await form.async_save(commit=False)
        user.zoho_id = form.zoho_id
        await user.asave()
        with ThreadPoolExecutor() as executor:
            executor.submit(login, self.request, user)
        return await super().form_valid(
            form
        )  # TODO change redirect url, may be use success_url field


class CustomLoginView(ApplicationMixin, AsyncLoginView):
    """Class view for user authentication."""

    redirect_authenticated_user = True
    next_page = "main_page:main_page"
    extra_context = {"title": "Sign in"}
    template_name = "custom_auth/sign_in.html"

    async def get_context_data(self, **kwargs: Any) -> dict:
        """Get context data for the view."""
        return await self.get_common_context(**await super().get_context_data(**kwargs))

    async def get(self, request, *args, **kwargs):
        """Handle GET requests: instantiate a blank version of the form."""
        context = await self.get_context_data(*args, **kwargs)
        if isinstance(context, HttpResponseServerError):
            return context
        return self.render_to_response(context)

    async def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """
        Is async because of the django.core.exceptions.ImproperlyConfigured exception.

        CustomLoginView HTTP handlers must either be all sync or all async.
        """
        return super().post(request, *args, **kwargs)

    async def put(self, *args: str, **kwargs: Any) -> HttpResponse:
        """
        Is async because of the django.core.exceptions.ImproperlyConfigured exception.

        CustomLoginView HTTP handlers must either be all sync or all async.
        """
        return super().put(*args, **kwargs)

    def form_valid(self, form: AuthenticationForm) -> HttpResponseRedirect:
        """Login user. Update 'Last_Activity_Time Zoho CRM customer field."""
        user: User = form.get_user()
        login(self.request, user)
        if user.zoho_id:
            custom_record_operations.update_record(
                module_api_name="customers",
                record_id=int(user.zoho_id),
                data={"Last_Activity_Time": datetime.now()},
            )
        return super().form_valid(form)


class CustomAsyncLoginView(AsyncLoginView):
    """Class view for user authentication with async functionality."""

    redirect_authenticated_user = True
    next_page = "main_page:main_page"
    extra_context = {"title": "Sign in"}
    template_name = "custom_auth/sign_in.html"

    async def form_valid(self, form: AsyncAuthenticationForm) -> HttpResponseRedirect:
        """Login user. Update 'Last_Activity_Time Zoho CRM customer field."""
        user: User = form.get_user()
        if user.zoho_id:
            await sync_to_async(custom_record_operations.update_record, thread_sensitive=False)(
                module_api_name="customers",
                record_id=int(user.zoho_id),
                data={"Last_Activity_Time": datetime.now()},
            )  # TODO change solution
            # TODO potential method to move to celery queue
        return await super().form_valid(form)


class ModPasswordChangeView(ApplicationMixin, PasswordChangeView):
    """Class view for user password changing."""

    success_url = reverse_lazy("custom_auth:signup")  # TODO for changing
    template_name = "custom_auth/password_change_form.html"
    extra_context = {"title": "Password change"}

    async def get_context_data(self, **kwargs: Any) -> dict:
        """Get context data for the view."""
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

        ModPasswordChangeView HTTP handlers must either be all sync or all async.
        """
        return super().post(request, *args, **kwargs)

    async def put(self, *args: str, **kwargs: Any) -> HttpResponse:
        """
        Is async because of the django.core.exceptions.ImproperlyConfigured exception.

        ModPasswordChangeView HTTP handlers must either be all sync or all async.
        """
        return super().put(*args, **kwargs)


class ModPasswordResetView(PasswordResetView):
    """Class view for resetting user password."""

    template_name = "custom_auth/password_reset_form.html"
    email_template_name = "custom_auth/password_reset_email.html"
    success_url = reverse_lazy("custom_auth:password_reset_done")
    extra_context = {"title": "Password reset"}


class ModPasswordResetDoneView(PasswordResetDoneView):
    """Modified PasswordResetDaneView."""

    template_name = "custom_auth/password_reset_done.html"
    extra_context = {"title": "Password reset"}


class ModPasswordResetConfirmView(PasswordResetConfirmView):
    """Modified PasswordResetConfirmView."""

    template_name = "custom_auth/password_reset_confirm.html"
    success_url = reverse_lazy("custom_auth:password_reset_complete")
    extra_context = {"title": "Password reset confirm"}


class ModPasswordResetCompleteView(PasswordResetCompleteView):
    """Modified PasswordResetCompleteView."""

    template_name = "custom_auth/password_reset_complete.html"
    extra_context = {"title": "Password reset done"}
