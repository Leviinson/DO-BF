"""Factories for testing 'zoho_token' app models."""

import factory

from tests.bases import BaseModelFactory
from zoho_token.models import ZohoOAuth


class ZohoOAuthFactory(BaseModelFactory):
    """Factory for testing ZohoOAuth model."""

    class Meta:
        model = ZohoOAuth

    client_id = factory.Faker("pystr", max_chars=60)
    client_secret = factory.Faker("pystr", max_chars=250)
    grant_token = factory.Faker("pystr", max_chars=250)
    refresh_token = factory.Faker("pystr", max_chars=250)
    redirect_url = factory.Faker("uri")
    access_token = factory.Faker("pystr", max_chars=250)
    token_id = factory.Faker("pystr", max_chars=100)
    expires_in = factory.Faker("pyint")
    user_email = factory.Faker("email")
