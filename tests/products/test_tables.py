"""Module for testing 'products' app models."""

import pytest

from products.models import ZohoImage, ZohoModuleRecord
from tests.bases import BaseModelFactory
from tests.products.factories import ZohoImageFactory, ZohoModuleRecordFactory


@pytest.mark.django_db
class TestZohoImage:
    """Class for testing ZohoImage model."""

    pytestmark = pytest.mark.django_db

    def test_factory(self) -> None:
        """Test ZohoImage model instances creation."""
        BaseModelFactory.check_factory(factory_class=ZohoImageFactory, model=ZohoImage)

    def test__str__(self) -> None:
        """Test ZohoImage __str__ method."""
        obj: ZohoImage = ZohoImageFactory()
        expected_result = f"{obj.image}"
        assert expected_result == obj.__str__()


@pytest.mark.django_db
class TestZohoModuleRecord:
    """Class for testing ZohoModuleRecord model."""

    pytestmark = pytest.mark.django_db

    def test_factory(self) -> None:
        """Test ZohoModuleRecord model instance creation."""
        BaseModelFactory.check_factory(
            factory_class=ZohoModuleRecordFactory, model=ZohoModuleRecord
        )

    def test__str__(self) -> None:
        """Test ZohoModuleRecord __str__ method."""
        obj: ZohoModuleRecord = ZohoModuleRecordFactory()
        expected_result = f"{obj.module_name} {obj.record_name}"
        assert expected_result == obj.__str__()
