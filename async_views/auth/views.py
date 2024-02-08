"""Async auth views."""
import warnings
from typing import Any, Dict, List, Optional, Set, Union

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import INTERNAL_RESET_SESSION_TOKEN, UserModel
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils.cache import add_never_cache_headers
from django.utils.deprecation import RemovedInDjango50Warning
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode
from django.utils.translation import gettext_lazy
from django.utils.translation import gettext_lazy as _

from async_forms.async_forms import AsyncForm
from async_views.auth.forms import (
    AsyncAuthenticationForm,
    AsyncPasswordChangeForm,
    AsyncPasswordResetForm,
    AsyncSetPasswordForm,
)
from async_views.auth.mixins import AsyncLoginRequiredMixin
from async_views.generic.base import AsyncTemplateView
from async_views.generic.edit import AsyncFormView


class AsyncRedirectURLMixin:
    """RedirectURLMixin async analog."""

    next_page: Optional[str] = None
    redirect_field_name: str = "next"
    success_url_allowed_hosts: Set = set()

    async def get_default_redirect_url(self) -> str:
        """Return the default redirect URL."""
        if self.next_page:
            return resolve_url(self.next_page)
        raise ImproperlyConfigured("No URL to redirect to. Provide a next_page.")

    async def get_redirect_url(self) -> str:
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name, self.request.GET.get(self.redirect_field_name)
        )
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=await self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ""

    async def get_success_url(self) -> str:
        """Get view success url."""
        return await self.get_redirect_url() or await self.get_default_redirect_url()

    async def get_success_url_allowed_hosts(self) -> Set:
        """Get view success url allowed hosts."""
        return {self.request.get_host(), *self.success_url_allowed_hosts}


class AsyncLoginView(AsyncRedirectURLMixin, AsyncFormView):
    """
    LoginView async analog.

    Display the login form and handle the login action.
    """

    authentication_form: Union[AsyncForm, AsyncAuthenticationForm, None] = None
    form_class: AsyncForm = AsyncAuthenticationForm
    redirect_authenticated_user: bool = False
    template_name: str = "registration/login.html"

    async def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse | HttpResponseRedirect:
        """
        Rewrite dispatch method.

        This method has 'never_cache' decorator, 'sensitive_post_parameters' decoarator
        implemented in the body. 'csrf_protect' decorator deleted from the decorators
        list, it's supposed csrf protection is enabled using CsrfViewMiddleware.
        """
        if not isinstance(request, HttpRequest):
            raise TypeError(
                "sensitive_post_parameters didn't receive an HttpRequest "
                "object. If you are decorating a classmethod, make sure "
                "to use @method_decorator."
            )
        request.sensitive_post_parameters = "__ALL__"
        # Implementation 'sensitive_post_parameters()' decorator
        # Change '__ALL__' to custom sensitiove parameters list

        if not hasattr(request, "META"):
            raise TypeError(
                "never_cache didn't receive an HttpRequest. If you are "
                "decorating a classmethod, be sure to use @method_decorator."
            )
        # Implementation 'never_cache' decorator

        user = await self.get_user_from_request(request)
        if self.redirect_authenticated_user and user.is_authenticated:
            redirect_to = await self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        response = await super().dispatch(request, *args, **kwargs)

        add_never_cache_headers(response)  # Implementation 'never_cache' decorator

        return response

    async def form_valid(
        self, form: AsyncForm | AsyncAuthenticationForm
    ) -> HttpResponseRedirect:
        """Security check complete. Log the user in."""
        await sync_to_async(auth_login, thread_sensitive=False)(self.request, form.get_user())
        return HttpResponseRedirect(await self.get_success_url())

    async def get_context_data(self, **kwargs: Any) -> Dict:
        """Get context data."""
        context = await super().get_context_data(**kwargs)
        current_site = await sync_to_async(get_current_site, thread_sensitive=False)(
            self.request
        )
        context.update(
            {
                self.redirect_field_name: await self.get_redirect_url(),
                "site": current_site,
                "site_name": current_site.name,
                **(self.extra_context or {}),
            }
        )
        return context

    async def get_default_redirect_url(self) -> str:
        """Return the default redirect URL."""
        if self.next_page:
            return resolve_url(self.next_page)
        else:
            return resolve_url(settings.LOGIN_REDIRECT_URL)

    async def get_form_class(self) -> AsyncForm | AsyncAuthenticationForm:
        """Get form class."""
        return self.authentication_form or self.form_class

    async def get_form_kwargs(self) -> Dict:
        """Get form kwargs."""
        kwargs = await super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class AsyncLogoutView(AsyncRedirectURLMixin, AsyncTemplateView):
    """
    LogoutView async analog.

    Log out the user and display the 'You are logged out' message.
    """

    http_method_names: List[str] = ["get", "head", "post", "options"]
    template_name: str = "registration/logged_out.html"

    async def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse | HttpResponseRedirect:
        """
        Rewrite dispatch method.

        'never_cache' decorator is implemented in the methods body.
        """
        if not hasattr(request, "META"):
            raise TypeError(
                "never_cache didn't receive an HttpRequest. If you are "
                "decorating a classmethod, be sure to use @method_decorator."
            )
        # Implementation 'never_cache' decorator

        if request.method.lower() == "get":
            warnings.warn(
                "Log out via GET requests is deprecated and will be removed in Django "
                "5.0. Use POST requests for logging out.",
                RemovedInDjango50Warning,
            )
        response = await super().dispatch(request, *args, **kwargs)

        add_never_cache_headers(response)  # Implementation 'never_cache' decorator

        return response

    async def get_context_data(self, **kwargs: Any) -> Dict:
        """Get context data."""
        context = await super().get_context_data(**kwargs)
        current_site = await sync_to_async(get_current_site, thread_sensitive=False)(
            self.request
        )
        context.update(
            {
                "site": current_site,
                "site_name": current_site.name,
                "title": _("Logged out"),
                "subtitle": None,
                **(self.extra_context or {}),
            }
        )
        return context

    async def get_default_redirect_url(self) -> str:
        """Return the default redirect URL."""
        if self.next_page:
            return resolve_url(self.next_page)
        elif settings.LOGOUT_REDIRECT_URL:
            return resolve_url(settings.LOGOUT_REDIRECT_URL)
        else:
            return self.request.path

    async def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse | HttpResponseRedirect:
        """
        Logout may be done via POST.

        csrf_protect decorator is supposed to be used in active CsrfViewMiddleware.
        """
        await sync_to_async(auth_logout, thread_sensitive=False)(request)
        redirect_to = await self.get_success_url()
        if redirect_to != request.get_full_path():
            # Redirect to target page once the session has been cleared.
            return HttpResponseRedirect(redirect_to)
        return await super().get(request, *args, **kwargs)


class AsyncPasswordContextMixin:
    """PasswordContextMixin async analog."""

    extra_context: Optional[Dict] = None

    async def get_context_data(self, **kwargs: Any) -> Dict:
        """Get context data."""
        context = await super().get_context_data(**kwargs)
        context.update({"title": self.title, "subtitle": None, **(self.extra_context or {})})
        return context


class AsyncPasswordChangeDoneView(
    AsyncPasswordContextMixin, AsyncLoginRequiredMixin, AsyncTemplateView
):
    """
    PasswordChahgeDoneView async analog.

    Render a template. Pass keyword arguments from the URLconf to the context.
    """

    template_name: str = "registration/password_change_done.html"
    title: str = gettext_lazy("Password change successful")

    async def get_context_data(self, **kwargs: Any) -> Dict:
        """Get context data."""
        context = await super().get_context_data(**kwargs)
        context.update({"title": self.title, "subtitle": None, **(self.extra_context or {})})
        return context


class AsyncPasswordChangeView(
    AsyncPasswordContextMixin, AsyncLoginRequiredMixin, AsyncFormView
):
    """
    PasswordChangeView async analog.

    A view for displaying a form and rendering a template response.
    """

    form_class: AsyncForm = AsyncPasswordChangeForm
    success_url: str = reverse_lazy("password_change_done")
    template_name: str = "registration/password_change_form.html"
    title: str = _("Password change")

    async def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse | HttpResponseRedirect:
        """
        Add decorators to dispatch.

        'csrf_protect' decorator is supposed to be used in active CsrfViewMiddleware.
        'sensitive_post_parameters()' decorator logic is implemented
         in the methods body.
        """
        if not isinstance(request, HttpRequest):
            raise TypeError(
                "sensitive_post_parameters didn't receive an HttpRequest "
                "object. If you are decorating a classmethod, make sure "
                "to use @method_decorator."
            )
        request.sensitive_post_parameters = "__ALL__"
        # Implementation 'sensitive_post_parameters()' decorator
        # Change '__ALL__' to custom sensitiove parameters list

        return await super().dispatch(request, *args, **kwargs)

    async def form_valid(self, form: AsyncPasswordChangeForm) -> HttpResponseRedirect:
        """Save user and perform super().form_valid actions."""
        await form.async_save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        await sync_to_async(auth_login, thread_sensitive=False)(self.request, form.user)
        # Changed update_session_auth_hash to login
        return await super().form_valid(form)

    async def get_form_kwargs(self) -> Dict:
        """Get form kwargs."""
        kwargs = await super().get_form_kwargs()
        kwargs["user"] = await sync_to_async(auth.get_user, thread_sensitive=False)(
            self.request
        )
        return kwargs


class AsyncPasswordResetCompleteView(AsyncPasswordContextMixin, AsyncTemplateView):
    """
    PasswordResetCompleteView async analog.

    Render a template. Pass keyword arguments from the URLconf to the context.
    """

    template_name: str = "registration/password_reset_complete.html"
    title: str = _("Password reset complete")

    async def get_context_data(self, **kwargs: Any) -> Dict:
        """Get context data."""
        context = await super().get_context_data(**kwargs)
        context["login_url"] = resolve_url(settings.LOGIN_URL)
        return context


class AsyncPasswordResetConfirmView(AsyncPasswordContextMixin, AsyncFormView):
    """
    PasswordResetConfirmView async analog.

    A view for displaying a form and rendering a template response.
    """

    form_class: AsyncForm = AsyncSetPasswordForm
    post_reset_login: bool = False
    post_reset_login_backend = None  # TODO set type hint
    reset_url_token: str = "set-password"
    success_url: str = reverse_lazy("password_reset_complete")
    template_name: str = "registration/password_reset_confirm.html"
    title = _("Enter new password")
    token_generator: PasswordResetTokenGenerator = PasswordResetTokenGenerator()

    async def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse | HttpResponseRedirect:
        """Rewrite dispatch, adding decorators and using token."""
        if not isinstance(request, HttpRequest):
            raise TypeError(
                "sensitive_post_parameters didn't receive an HttpRequest "
                "object. If you are decorating a classmethod, make sure "
                "to use @method_decorator."
            )
        request.sensitive_post_parameters = "__ALL__"
        # Implementation 'sensitive_post_parameters()' decorator
        # Change '__ALL__' to custom sensitiove parameters list

        if not hasattr(request, "META"):
            raise TypeError(
                "never_cache didn't receive an HttpRequest. If you are "
                "decorating a classmethod, be sure to use @method_decorator."
            )
        # Implementation 'never_cache' decorator

        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )
        self.validlink = False
        self.user = await self.get_user(kwargs["uidb64"])
        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = await sync_to_async(
                    self.request.session.get, thread_sensitive=False
                )(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    response = await super().dispatch(request, *args, **kwargs)
                    add_never_cache_headers(response)  # Implementation 'never_cache' decorator
                    return response
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    await self.modify_request_session(token)
                    # self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    response = HttpResponseRedirect(redirect_url)
                    add_never_cache_headers(response)  # Implementation 'never_cache' decorator
                    return response
        # Display the "Password reset unsuccessful" page.
        response = self.render_to_response(await self.get_context_data())
        add_never_cache_headers(response)  # Implementation 'never_cache' decorator
        return response

    @sync_to_async(thread_sensitive=False)
    def modify_request_session(self, token: str) -> None:
        """Modify request session."""
        self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token

    async def form_valid(self, form: AsyncSetPasswordForm) -> HttpResponseRedirect:
        """Save user."""
        user = await form.async_save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            sync_to_async(auth_login, thread_sensitive=False)(
                self.request, user, self.post_reset_login_backend
            )
        return await super().form_valid(form)

    async def get_context_data(self, **kwargs: Any) -> Dict:
        """Get context data."""
        context = await super().get_context_data(**kwargs)
        if self.validlink:
            context["validlink"] = True
        else:
            context.update(
                {
                    "form": None,
                    "title": _("Password reset unsuccessful"),
                    "validlink": False,
                }
            )
        return context

    async def get_form_kwargs(self) -> Dict:
        """Get form kwargs."""
        kwargs = await super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    @staticmethod
    async def get_user(uidb64: str) -> UserModel:
        """Get default user."""
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = await UserModel._default_manager.aget(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            UserModel.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user


class AsyncPasswordResetDoneView(AsyncPasswordContextMixin, AsyncTemplateView):
    """
    PasswordResetDone async analog.

    Render a template. Pass keyword arguments from the URLconf to the context.
    """

    template_name: str = "registration/password_reset_done.html"
    title: str = _("Password reset sent")


class AsyncPasswordResetView(AsyncPasswordContextMixin, AsyncFormView):
    """
    PasswordResetView async analog.

    A view for displaying a form and rendering a template response.
    """

    email_template_name: str = "registration/password_reset_email.html"
    extra_email_context: Optional[Dict] = None
    form_class = AsyncPasswordResetForm
    from_email: Optional[str] = None
    html_email_template_name: Optional[str] = None
    subject_template_name: str = "registration/password_reset_subject.txt"
    success_url: str = reverse_lazy("password_reset_done")
    template_name: str = "registration/password_reset_form.html"
    title: str = _("Password reset")
    token_generator: PasswordResetTokenGenerator = PasswordResetTokenGenerator()

    async def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse | HttpResponseRedirect:
        """
        Rewrite dispatch, adding decorator.

        'csrf_protect' decorator logic is supposed to be used in
        active CsrfViewMiddleware.
        """
        return await super().dispatch(request, *args, **kwargs)

    async def form_valid(self, form: AsyncPasswordResetForm) -> HttpResponseRedirect:
        """Save form with async functionality."""
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }
        await form.async_save(**opts)
        return await super().form_valid(form)
