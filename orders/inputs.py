"""
This module provides a custom CheckboxHiddenInput class for use in Django forms.

Usage:
    from your_module import CheckboxHiddenInput

    class YourForm(forms.Form):
        your_field = forms.BooleanField(widget=CheckboxHiddenInput())
"""
from django import forms


class CheckboxHiddenInput(forms.CheckboxInput):
    """
    Custom CheckboxInput class to render a hidden checkbox in Django forms.

    Attributes:
        attrs (dict): A dictionary of HTML attributes for the widget.
        check_test (callable): A function to determine whether the checkbox is checked.

    Example:
        class YourForm(forms.Form):
            your_field = forms.BooleanField(widget=CheckboxHiddenInput())
    """

    def __init__(self, attrs=None, check_test=None):
        """
        Initialize the CheckboxHiddenInput.

        Args:
            attrs (dict): A dictionary of HTML attributes for the widget.
            check_test (callable): A function to determine whether the checkbox is checked.
        """
        attrs = attrs or {}
        attrs["hidden"] = True
        super().__init__(attrs, check_test)
