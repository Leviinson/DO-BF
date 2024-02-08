"""Module for testing 'mainpage' app models."""

import pytest

from mainpage.models import Contact, CustomCategories, MainSlider, SeoBlock
from tests.bases import BaseModelFactory
from tests.mainpage.factories import (
    ContactFactory,
    CustomCategoriesFactory,
    MainSliderFactory,
    SeoBlockFactory,
)


@pytest.mark.django_db
class TestContact:
    """Class for testing Contact model."""

    pytestmark = pytest.mark.django_db

    def test_factory(self) -> None:
        """Test Contact model instances creation."""
        BaseModelFactory.check_factory(factory_class=ContactFactory, model=Contact)

    def test__str__(self) -> None:
        """Test Contact __str__ method."""
        obj: Contact = ContactFactory()
        expected_result = "Contacts info"
        assert expected_result == obj.__str__()


@pytest.mark.django_db
class TestSeoBlock:
    """Class for testing SeoBlock model."""

    pytestmark = pytest.mark.django_db

    def test_factory(self) -> None:
        """Test SeoBlock model instances creation."""
        BaseModelFactory.check_factory(factory_class=SeoBlockFactory, model=SeoBlock)

    def test__str__(self) -> None:
        """Test SeoBlock __str__ method."""
        obj: SeoBlock = SeoBlockFactory()
        expected_result = str(obj.description)
        assert expected_result == obj.__str__()


@pytest.mark.django_db
class TestMainSlider:
    """Class for testing MainSlider model."""

    pytestmark = pytest.mark.django_db

    def test_factory(self) -> None:
        """Test MainSlider model instances creation."""
        BaseModelFactory.check_factory(factory_class=MainSliderFactory, model=MainSlider)

    def test__str__(self) -> None:
        """Test MainSlider __str__ method."""
        obj: MainSlider = MainSliderFactory()
        expected_result = str(obj.button)
        assert expected_result == obj.__str__()


@pytest.mark.django_db
class TestCustomCategories:
    """Class for testing CustomCategories model."""

    pytestmark = pytest.mark.django_db

    def test_factory(self) -> None:
        """Test CustomCategories model instances creation."""
        BaseModelFactory.check_factory(
            factory_class=CustomCategoriesFactory, model=CustomCategories
        )

    def test__str__(self) -> None:
        """Test CustomCategories __str__ method."""
        obj: CustomCategories = CustomCategoriesFactory()
        expected_result = str(obj.title)
        assert expected_result == obj.__str__()
