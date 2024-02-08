"""Module for 'custom_auth' app validators."""
import re

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


def phone_number_validator(
    value: str,
) -> None:  # TODO change, depends on frontend library
    """Validate phone number."""
    if not re.match("[0-9+ ]{5,20}", value):
        raise ValidationError(
            {
                "Error": "Phone number must consists of digits, space and '+' mark,"
                " 5-20 character length."
            }
        )


username_validator = UnicodeUsernameValidator()
