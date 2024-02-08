"""Factories for testing 'mainpage' app models."""

import factory

from mainpage.models import Contact, CustomCategories, MainSlider, SeoBlock
from tests.bases import BaseModelFactory


class ContactFactory(BaseModelFactory):
    """Factory for testing Contact model."""

    class Meta:
        model = Contact

    international_phone_number = factory.Faker("phone_number")


class SeoBlockFactory(BaseModelFactory):
    """Factory for testing SeoBlock model."""

    class Meta:
        model = SeoBlock

    description = factory.Faker("pystr", min_chars=1, max_chars=255)
    picture = factory.django.ImageField(color=factory.Faker("color"))
    button = factory.Faker("pystr", min_chars=1, max_chars=50)
    link = factory.Faker("url")


class MainSliderFactory(BaseModelFactory):
    """Factory for testing MainSlider model."""

    class Meta:
        model = MainSlider

    description_up = factory.Faker("pystr", min_chars=1, max_chars=255)
    description_down = factory.Faker("pystr", min_chars=1, max_chars=255)
    picture = factory.django.ImageField(color=factory.Faker("color"))
    button = factory.Faker("pystr", min_chars=1, max_chars=50)
    link = factory.Faker("pystr", max_chars=15)
    ordinal_number = factory.Sequence(lambda x: x)


class CustomCategoriesFactory(BaseModelFactory):
    """Factory for testing CustomCategory model."""

    class Meta:
        model = CustomCategories

    title = factory.Faker("pystr", min_chars=1, max_chars=15)
    link = factory.Faker("uri")
    ordinal_number = factory.Sequence(lambda x: x)
