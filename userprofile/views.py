"""Function and class views for 'userprofile' app."""
from typing import Any

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from services.crm_interface import custom_record_operations
from userprofile.app_services.crm_utils import crm_formatters
from userprofile.app_services.mixins import (
    AsyncUserProfileFormView,
    UserProfileFormView,
    UserProfileTemplateView,
)
from userprofile.app_services.userprofile_handlers import user_handlers
from userprofile.forms import (
    AddressDeleteForm,
    AddressForm,
    AsyncUserProfileForm,
    ContactDeleteForm,
    ContactForm,
    UserProfileForm,
)

from .app_services.data_getters import crm_data


class UserProfileView(UserProfileTemplateView):
    """Class view for showing user information."""

    template_name = "userprofile/user_info.html"
    extra_context = {"title": "User account"}

    async def get_context_data(self, **kwargs: Any) -> dict:
        """Get context data for the view."""
        context = await super().get_context_data(**kwargs)
        user = self.request.user
        initial = {
            "username": user.username,
            "phone_number": user.phone_number,
            "email": user.email,
        }
        context["user_form"] = UserProfileForm(initial=initial)
        return context


class UserProfileUpdateView(UserProfileFormView):
    """Class view for user data changing."""

    form_class = UserProfileForm
    template_name = "userprofile/user_change_form.html"
    extra_context = {"title": "Change user data"}
    success_url = "userprofile:account"

    def get_initial(self) -> dict:
        """Return the initial data to use for forms on this view."""
        initial: dict = super().get_initial()
        user = self.request.user
        initial.update(
            {
                "username": user.username,
                "phone_number": user.phone_number,
                "email": user.email,
                "zoho_id": user.zoho_id,
            }
        )
        return initial

    def form_valid(self, form: UserProfileForm) -> HttpResponseRedirect:
        """Redirect to the supplied URL, if the form is valid."""
        self.request.user.username = form.cleaned_data.get("username")
        self.request.user.phone_number = form.cleaned_data.get("phone_number")
        self.request.user.email = form.cleaned_data.get("email")
        self.request.user.save()
        return super().form_valid(form)


class AsyncUserProfileUpdateView(AsyncUserProfileFormView):
    """Class view for user data changing with async_views functionality."""

    form_class = AsyncUserProfileForm
    template_name = "userprofile/user_change_form.html"
    extra_context = {"title": "Change user data"}
    success_url = "userprofile:account"
    view_is_async = True

    async def get_initial(self) -> dict:
        """Return the initial data to use for forms on this view."""
        initial: dict = await super().get_initial()
        user = await self.get_user_from_request(self.request)
        initial.update(
            {
                "username": user.username,
                "phone_number": user.phone_number,
                "email": user.email,
                "zoho_id": user.zoho_id,
            }
        )
        return initial

    async def form_valid(self, form: AsyncUserProfileForm) -> HttpResponseRedirect:
        """Redirect to the supplied URL, if the form is valid."""
        await form.async_save()
        return await super().form_valid(form)

    async def get_form_kwargs(self):
        """Add model pk to form kwargs."""
        kwargs = await super().get_form_kwargs()
        user = await self.get_user_from_request(self.request)
        kwargs.update({"instance": user})
        return kwargs


@method_decorator(never_cache, name="dispatch")
class AddressView(UserProfileTemplateView):
    """Class view to get customer addresses from Zoho CRM."""

    template_name = "userprofile/addresses.html"

    async def get_context_data(self, **kwargs: Any) -> dict:
        """Get context data for the view."""
        context = await self.get_context_data(**kwargs)
        context["addresses"] = await crm_data.get_customer_addresses(self.request.user.zoho_id)
        return context


class AddressUpdateView(UserProfileFormView):
    """Class view for updating customer address."""

    form_class = AddressForm
    template_name = "userprofile/address_update_form.html"
    extra_context = {"title": "Update customer address"}
    success_url = "userprofile:addresses"

    async def get_initial(self) -> dict:
        """Return the initial data to use for forms on this view."""
        initial: dict = super().get_initial()
        address = await crm_data.get_customer_address(self.kwargs["address_id"])
        if address:
            address["name"] = address.get("Name")
            initial.update(address)
        return initial

    async def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
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

    async def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**await self.get_form_kwargs())

    async def get_context_data(self, **kwargs: Any) -> dict:
        """Get context data for the view."""
        if "form" not in kwargs:
            kwargs["form"] = await self.get_form()
        context = await self.get_context_data(**kwargs)
        address_id = self.kwargs.get("address_id")
        context["address_id"] = address_id
        context["delete_form"] = AddressDeleteForm(initial={"id": address_id})
        return context

    async def post(self, request, *args, **kwargs):
        """
        To instantiate a form instance with the passed POST vars.

        To check if it's valid.
        """
        form = await self.get_form()
        if form.is_valid():
            return await self.form_valid(form)
        else:
            return self.form_invalid(form)

    async def form_valid(self, form: AddressForm) -> HttpResponseRedirect:
        """
        Redirect to the success url if the form is valid.

        Perform updating data in Zoho CRM.
        """
        data = form.cleaned_data
        data["Name"] = data.pop("name")
        if "is_default" in form.changed_data and data.get("is_default"):
            addresses = await crm_data.get_customer_default_address(self.request.user.zoho_id)
            for address in addresses:
                custom_record_operations.update_record(
                    "customer_addresses",
                    int(address.get("id")),
                    {"is_default": False, "Name": address.get("Name")},
                )
        custom_record_operations.update_record(
            "customer_addresses", self.kwargs.get("address_id"), data
        )
        return super().form_valid(form)


class AddressCreateView(UserProfileFormView):
    """Class view for creating customer address."""

    form_class = AddressForm
    template_name = "userprofile/address_create_form.html"
    extra_context = {"title": "Create customer address"}
    success_url = "userprofile:addresses"

    async def get_context_data(self, **kwargs: Any) -> dict:
        """Get context data for the view."""
        return await self.get_common_context(**super().get_context_data(**kwargs))

    async def post(self, request, *args, **kwargs):
        """
        To instantiate a form instance with the passed POST vars.

        To check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return await self.form_valid(form)
        else:
            return self.form_invalid(form)

    async def form_valid(self, form: AddressForm) -> HttpResponseRedirect:
        """
        Redirect to the success url if the form is valid.

        Perform updating data in Zoho CRM.
        """
        data = form.cleaned_data
        if data.get("is_default"):
            addresses = await crm_data.get_customer_default_address(self.request.user.zoho_id)
            for address in addresses:
                custom_record_operations.update_record(
                    "customer_addresses",
                    int(address.get("id")),
                    {"is_default": False, "Name": address.get("Name")},
                )
        crm_formatters.prepare_address_contact_creation_data(data, self.request.user.zoho_id)
        await custom_record_operations.create_records(
            "customer_addresses",
            [
                data,
            ],
        )
        return super().form_valid(form)


class AddressDeleteView(UserProfileFormView):
    """Class view for deleting customer address."""

    form_class = AddressDeleteForm
    template_name = "userprofile/address_update_form.html"
    success_url = "userprofile:addresses"

    def form_valid(self, form: AddressDeleteForm) -> HttpResponseRedirect:
        """
        Redirect to the success url if the form is valid.

        Perform deleting record in Zoho CRM module.
        """
        data = form.cleaned_data
        custom_record_operations.delete_record("customer_addresses", int(data.get("id")))
        return super().form_valid(form)

    async def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect:
        """
        Rewrite class get method to return get_success_url redirection.

        Is async because of this one exception:
        django.core.exceptions.ImproperlyConfigured:
        AddressDeleteView HTTP handlers must either be all sync or all async.
        """
        return HttpResponseRedirect(self.get_success_url())


# @method_decorator(never_cache, name="dispatch") TODO: translate to async way of using
class ContactView(UserProfileTemplateView):
    """Class view to get customer contacts from Zoho CRM."""

    template_name = "userprofile/contacts.html"
    extra_context = {"title": "Contacts"}

    async def get_context_data(self, **kwargs: Any) -> dict:
        """Get context data for the view."""
        context = await super().get_context_data(**kwargs)
        context = await self.get_common_context(**context)
        user = await sync_to_async(get_user)(self.request)
        context["contacts"] = await crm_data.get_customer_contacts(user.zoho_id)
        return context


class ContactUpdateView(UserProfileFormView):
    """Class view for changing customer address."""

    form_class = ContactForm
    template_name = "userprofile/contact_update_form.html"
    extra_context = {"title": "Update customer contact"}
    success_url = "userprofile:contacts"

    async def get_initial(self) -> dict:
        """Return the initial data to use for forms on this view."""
        initial: dict = super().get_initial()
        contact = await crm_data.get_customer_contact(self.kwargs["contact_id"])
        if contact:
            contact["name"] = contact.get("Name")
            initial.update(contact)
        return initial

    async def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
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

    async def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**await self.get_form_kwargs())

    async def get_context_data(self, **kwargs: Any) -> dict:
        """Get context data for the view."""
        if "form" not in kwargs:
            kwargs["form"] = await self.get_form()
        context = await self.get_context_data(**kwargs)
        contact_id = self.kwargs.get("contact_id")
        context["contact_id"] = contact_id
        context["delete_form"] = AddressDeleteForm(initial={"id": contact_id})
        return context

    def form_valid(self, form: ContactForm) -> HttpResponseRedirect:
        """
        Redirect to the success url if the form is valid.

        Perform updating data in Zoho CRM.
        """
        data = form.cleaned_data
        data["Name"] = data.pop("name")
        custom_record_operations.update_record(
            "customer_contacts", self.kwargs.get("contact_id"), data
        )
        return super().form_valid(form)


class ContactCreateView(UserProfileFormView):
    """Class view for creating customer contact."""

    form_class = ContactForm
    template_name = "userprofile/contact_create_form.html"
    extra_context = {"title": "Create customer contact"}
    success_url = "userprofile:contacts"

    async def get_context_data(self, **kwargs: Any) -> dict:
        """Get context data for the view."""
        return await self.get_context_data(**kwargs)

    async def form_valid(self, form: ContactForm) -> HttpResponseRedirect:
        """
        Redirect to the success url if the form is valid.

        Perform updating data in Zoho CRM.
        """
        data = form.cleaned_data
        crm_formatters.prepare_address_contact_creation_data(data, self.request.user.zoho_id)
        await custom_record_operations.create_records(
            "customer_contacts",
            [
                data,
            ],
        )
        return super().form_valid(form)


class ContactDeleteView(UserProfileFormView):
    """Class view for deleting customer contact."""

    form_class = ContactDeleteForm
    template_name = "userprofile/contact_update_form.html"
    success_url = "userprofile:contacts"

    def form_valid(self, form: ContactDeleteForm) -> HttpResponseRedirect:
        """
        Redirect to the success url if the form is valid.

        Perform deleting record in Zoho CRM module.
        """
        data = form.cleaned_data
        custom_record_operations.delete_record("customer_contacts", int(data.get("id")))
        return super().form_valid(form)

    async def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect:
        """
        Rewrite class get method to return get_success_url redirection.

        Is async because of this one exception:
        django.core.exceptions.ImproperlyConfigured:
        ContactDeleteView HTTP handlers must either be all sync or all async.
        """
        return HttpResponseRedirect(self.get_success_url())


class ViewedCustomerProductsView(UserProfileTemplateView):
    """Class view for get customer viewed product list."""

    template_name = "userprofile/viewed_customer_product_list.html"
    extra_context = {"title": "Products"}

    async def get_context_data(self, **kwargs: Any) -> dict:
        """Get context data for the view."""
        context = await self.get_context_data(**kwargs)
        context["products"] = await user_handlers.get_and_refresh_viewed_customer_products(
            self.request.user.id
        )
        #   TODO Hence this view is not used now, get_and_refresh... calling is not correct
        return context
