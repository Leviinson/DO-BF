"""Factories for testing 'custom_auth' app models."""

import factory

from custom_auth.models import User
from tests.bases import BaseModelFactory


class UserFactory(BaseModelFactory):
    """Factory for testing custom User model."""

    class Meta:
        model = User

    username = factory.Faker("user_name")
    phone_number = factory.Faker("phone_number")
    email = factory.Faker("email")
    zoho_id = factory.Faker("random_int", min=1000, max=9223372036854775807)
    is_staff = factory.Faker("pybool")
    is_active = factory.Faker("pybool")
    date_joined = factory.Faker("date_time")
