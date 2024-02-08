"""Forms for 'userprofile' app."""
from typing import Any

from asgiref.sync import sync_to_async
from django import forms
from django.core.exceptions import ValidationError

from async_forms.async_forms import AsyncModelForm
from custom_auth.models import User
from services.crm_interface import custom_record_operations
from services.utils import formatters


class UserProfileForm(forms.ModelForm):
    """Form for userprofile view."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Rewrite __init__ method with changing some fields widgets."""
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = None
        self.fields["phone_number"].help_text = None
        self.fields["zoho_id"].widget = forms.HiddenInput()

    def clean(self, *args, **kwargs):
        """Clean form data."""
        cleaned_data = super().clean()
        if (
            not User.objects.exclude(zoho_id=cleaned_data.get("zoho_id"))
            .filter(phone_number=cleaned_data.get("phone_number"))
            .exists()
        ):
            self._validate_unique = False
        return cleaned_data

    def _post_clean(self):
        """
        Check if there are any errors.

        If any errors or if there are some problem with connection with
        Zoho CRM, return error message, otherwise change user data in Zoho CRM.
        """
        super()._post_clean()
        response: int = 0
        if not self._errors:
            response = custom_record_operations.update_record(
                module_api_name="customers",
                record_id=self.cleaned_data.get("zoho_id"),
                data=formatters.format_user_data(self.cleaned_data),
            )
        if not response:
            self._update_errors(ValidationError("Something went wrong. Please, try again!"))

    class Meta:
        """Class Meta for UserProfileForm."""

        model = User
        fields = (
            "username",
            "phone_number",
            "email",
            "zoho_id",
        )


class AddressForm(forms.Form):
    """Form class for creation and update customer address."""

    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Address name",
            }
        ),
    )
    country = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Country",
            }
        ),
    )
    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "City",
            }
        ),
    )
    street = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Street",
            }
        ),
    )
    building = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Building",
            }
        ),
    )
    appartment = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Apartment",
            }
        ),
    )
    is_default = forms.BooleanField(required=False)


class AddressDeleteForm(forms.Form):
    """Form class for deleting customer address record."""

    id = forms.IntegerField(widget=forms.HiddenInput())


class ContactForm(forms.Form):
    """Form class for creation and changing customer contact."""

    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Contact person",
            }
        ),
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Phone number",
            }
        ),
    )


class ContactDeleteForm(forms.Form):
    """Form class for deletion customer contact."""

    id = forms.IntegerField(widget=forms.HiddenInput())


class AsyncUserProfileForm(AsyncModelForm):
    """Form for userprofile view. Async functionality."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Rewrite __init__ method with changing some fields widgets."""
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = None
        self.fields["phone_number"].help_text = None
        self.fields["zoho_id"].widget = forms.HiddenInput()

    async def _async_post_clean(self) -> None:
        """
        Check if there are any errors.

        If any errors or if there are some problem with connection with
        Zoho CRM, return error message, otherwise change user data in Zoho CRM.
        """
        await super()._async_post_clean()
        response: int = 0
        if not self._errors:
            response = await sync_to_async(
                custom_record_operations.update_record, thread_sensitive=False
            )(
                module_api_name="customers",
                record_id=self.cleaned_data.get("zoho_id"),
                data=formatters.format_user_data(self.cleaned_data),
            )
        if not response:
            self.add_error(
                None,
                ValidationError({"Error": "Something went wrong. Please, try again!"}),
            )

    class Meta:
        """Class Meta for AsyncUserProfileForm class."""

        model = User
        fields = ("username", "phone_number", "email", "zoho_id")
