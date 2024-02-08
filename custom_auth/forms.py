"""Module for 'custom_auth' api forms."""
from typing import Any, Optional

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from async_forms import async_forms
from custom_auth.models import User
from services.crm_interface import custom_record_operations
from services.utils import formatters


class CustomUserCreationForm(async_forms.AsyncModelForm):
    """Custom user creation form."""

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        """Class Meta for CustomUserCreationForm."""

        model = User
        fields = ("username", "phone_number", "email")
        field_classes = {"username": UsernameField}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create additional instance attribute for zoho_id storage."""
        super().__init__(*args, **kwargs)
        self.zoho_id: Optional[int] = None
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs["autofocus"] = True

    def clean_password2(self) -> str:
        """Check password."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    async def _post_clean(self) -> None:
        """
        Modificate password checking.

        Create Zoho CRM customer instance, get instance id for saving in
        local db user instance. In case of issues with Zoho CRM customer
        instance creation get error message in form general errors message
        field. Unique username and phone_number properties are taken into
        account also.
        """
        await super()._async_post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password2", error)
        if not self._errors:
            self.zoho_id = await custom_record_operations.create_records(
                module_api_name="customers",
                data=[formatters.format_user_data(self.cleaned_data)],
            )
        if not self.zoho_id:
            self._update_errors(ValidationError("Something went wrong. Please, try again!"))

    async def async_save(self, commit: bool = True) -> User:
        """Save user with commit options."""
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate."
                % (
                    self.instance._meta.object_name,
                    "created" if self.instance._state.adding else "changed",
                )
            )
        user = self.instance
        user.set_password(self.cleaned_data["password1"])
        if commit:
            await user.asave()
        return user
