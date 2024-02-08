from django import forms

from async_forms.async_forms import AsyncForm


class AsyncLocationForm(AsyncForm):
    """Form for handling location information."""

    country = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {
                "id": "autocompleteCountryLocation",
            }
        ),
        required=True,
    )
    region = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {
                "id": "autocompleteRegionLocation",
            }
        ),
        required=True,
    )
    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {
                "id": "autocompleteCityLocation",
            }
        ),
        required=True,
    )
