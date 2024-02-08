"""Module for testing custom_auth app tables."""
import pytest

from custom_auth.models import User
from tests.bases import BaseModelFactory
from tests.custom_auth.factories import UserFactory


@pytest.mark.django_db
class TestUser:
    """Class for testing User model."""

    pytestmark = pytest.mark.django_db

    def test_factory(self) -> None:
        """Test User model instances creation."""
        BaseModelFactory.check_factory(factory_class=UserFactory, model=User)

    def test__str__(self) -> None:
        """Test User __str__ method."""
        obj: User = UserFactory()
        expected_result = str(obj.username)
        assert expected_result == obj.__str__()
