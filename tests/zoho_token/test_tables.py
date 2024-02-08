"""Module for testing 'zoho_token' app models."""

import pytest

from tests.bases import BaseModelFactory
from tests.zoho_token.factories import ZohoOAuthFactory
from zoho_token.models import ZohoOAuth


@pytest.mark.django_db
class TestZohoOAuth:
    """Class for testing ZohoOAuth model."""

    pytestmark = pytest.mark.django_db

    def test_factory(self) -> None:
        """Test ZohoOAuth model instances creation."""
        BaseModelFactory.check_factory(factory_class=ZohoOAuthFactory, model=ZohoOAuth)

    def test__str__(self) -> None:
        """Test ZohoOAuth __str__ method."""
        obj: ZohoOAuth = ZohoOAuthFactory()
        expected_result: str = str(obj.user_email)
        assert expected_result == obj.__str__()
