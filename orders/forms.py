"""Contains form for checkout view."""

import json

import phonenumbers
from django import forms
from django.core.exceptions import ValidationError

from async_forms.async_forms import AsyncForm

from .inputs import CheckboxHiddenInput


class AsyncCheckoutForm(AsyncForm):
    """Form for handling checkout information."""

    customer_phone_number = forms.CharField(
        max_length=25,
        widget=forms.HiddenInput(
            {
                "class": "order-tel-hidden",
            }
        ),
    )
    customer_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {
                "class": "p-16-auto-regular darck-gray input-text order-customer-name",
                "placeholder": "Ім’я та прізвище",
            }
        ),
    )
    customer_email = forms.EmailField(
        max_length=120,
        widget=forms.EmailInput(
            {
                "class": "p-16-auto-regular darck-gray input-text order-customer-email",
                "placeholder": "Email",
            }
        ),
        required=False,
    )

    recipient_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {
                "class": "p-16-auto-regular darck-gray input-text order-recipient-name",
                "placeholder": "Ім’я одержувача ...",
            }
        ),
        required=False,
    )
    recipient_phone_number = forms.CharField(
        max_length=25,
        widget=forms.HiddenInput(
            {
                "class": "order-tel-hidden",
            }
        ),
        required=False,
    )

    is_anonym = forms.BooleanField(
        widget=forms.CheckboxInput(
            {"id": "switchAnonym"},
        ),
        initial=False,
        required=False,
    )
    is_surprise = forms.BooleanField(
        widget=forms.CheckboxInput({"id": "switchIsSurprise"}), initial=False, required=False
    )
    ask_recipient_address = forms.BooleanField(
        widget=forms.CheckboxInput({"id": "switchAddress"}), initial=False, required=False
    )
    recipient_is_customer = forms.BooleanField(
        widget=CheckboxHiddenInput(
            {
                "class": "p-16-auto-medium darck-gray input-text",
                "id": "isRecipientCustomer",
            },
        ),
        initial=False,
        required=False,
    )
    recipient_is_not_customer = forms.BooleanField(
        widget=CheckboxHiddenInput(
            {
                "class": "p-16-auto-medium darck-gray input-text",
                "id": "isRecipientNotCustomer",
            },
        ),
        initial=True,
        required=False,
    )

    country = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {
                "class": "p-16-auto-regular darck-gray input-text order-country",
                "placeholder": "Країна ...",
                "id": "autocompleteCountry",
            }
        ),
        required=False,
    )
    region = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {
                "class": "p-16-auto-regular darck-gray input-text order-region",
                "placeholder": "Область ...",
                "id": "autocompleteRegion",
            }
        ),
        required=False,
    )
    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {
                "class": "p-16-auto-regular darck-gray input-text order-city",
                "placeholder": "Місто ...",
                "id": "autocompleteCity",
            }
        ),
        required=False,
    )
    address = forms.CharField(
        max_length=80,
        widget=forms.HiddenInput(
            {
                "class": "order-address",
            }
        ),
        required=False,
    )
    flat = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            {
                "class": "p-16-auto-regular darck-gray input-text order-flat",
                "placeholder": "Поміщення ...",
            }
        ),
        required=False,
    )
    date = forms.DateField(
        widget=forms.DateInput(
            {"type": "date", "class": "p-16-auto-regular darck-gray input-text order-date"}
        ),
    )

    postcard = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(
            {"class": "input-text order-postcard", "placeholder": "Текст листівки ..."}
        ),
    )
    selected_currency = forms.CharField(widget=forms.HiddenInput())

    async def async_clean(self):
        """To perform asynchronous form validation.

        This method is responsible for performing additional validation checks
        beyond the standard synchronous clean() method. It is designed for
        handling asynchronous validation, such as making database queries or
        external API calls.

        Returns:
            dict: A dictionary containing the cleaned form data after validation.

        Raises:
            ValidationError: If any validation error occurs, a
                ValidationError is raised with an appropriate error message.

        Example:
            The method checks various conditions related to recipient information,
            delivery address, and other form fields, raising ValidationError if
            any inconsistency is detected.
        """
        cleaned_data = await super().async_clean()
        if not (
            cleaned_data["recipient_is_customer"] ^ cleaned_data["recipient_is_not_customer"]
        ):
            raise ValidationError(
                "Fields 'recipient is customer', 'recipient is not customer' checked/unchecked."
            )
        if cleaned_data["recipient_is_customer"] and (
            cleaned_data["recipient_name"] or cleaned_data["recipient_phone_number"]
        ):
            raise ValidationError(
                "Fields 'recipient name' and 'recipient phone number "
                "can't be filled together with 'is customer recipient' field."
            )

        elif cleaned_data["recipient_is_not_customer"] and (
            not cleaned_data["recipient_name"] or not cleaned_data["recipient_phone_number"]
        ):
            raise ValidationError(
                """Fields 'recipient name' and 'recipient phone number'
                both must be filled together with 'is customer recipient' field."""
            )
        if not cleaned_data["ask_recipient_address"] and (
            not cleaned_data.get("country")
            or not cleaned_data.get("region")
            or not cleaned_data.get("city")
            or not cleaned_data.get("address")
            or not cleaned_data.get("flat")
        ):
            raise ValidationError(
                f"You address isn't specified and 'ask recipient address' option " f"unchecked."
            )
        if not cleaned_data.get("date"):
            raise ValidationError("Delivery date isn't specified.")

        if cleaned_data.get("address"):
            try:
                cleaned_data["address"] = json.loads(cleaned_data["address"])
            except json.JSONDecodeError:
                raise ValidationError("Server error occured while validating address.")
        return cleaned_data

    def clean_recipient_phone_number(self):
        """
        Clean and parse the recipient's phone number.

        Returns:
            int: The cleaned and parsed recipient's phone number.
        """
        if phone_number := self.cleaned_data.get("recipient_phone_number"):
            return self._parse_phone_number(phone_number)
        return phone_number

    def clean_customer_phone_number(self):
        """
        Clean and parse the buyer's phone number.

        Returns:
            int: The cleaned and parsed buyer's phone number.
        """
        return self._parse_phone_number(self.cleaned_data.get("customer_phone_number"))

    @staticmethod
    def _parse_phone_number(phone_number: str):
        """
        Parse and validate a phone number using phonenumbers library.

        Args:
            phone_number (str): The phone number to parse and validate.

        Returns:
            int: The parsed and validated phone number.

        Raises:
            ValidationError: If the phone number has an invalid format.
        """
        z = phonenumbers.parse(phone_number, keep_raw_input=True)
        if not phonenumbers.is_valid_number(z):
            raise ValidationError("Wrong phone number format.")
        return phonenumbers.format_number(z, phonenumbers.PhoneNumberFormat.E164)
