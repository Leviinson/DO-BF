"""Factories for testing 'product' app models."""

import factory

from products.models import ZohoImage, ZohoModuleRecord
from tests.bases import BaseModelFactory


class ZohoModuleRecordFactory(BaseModelFactory):
    """Factory for testing ZohoModuleRecord model."""

    class Meta:
        model = ZohoModuleRecord
        exclude = ("zohoimage_set",)

    id = factory.Faker("random_int", min=1000, max=9223372036854775807)
    module_name = factory.Faker("pystr", min_chars=2, max_chars=100)
    record_name = factory.Faker("pystr", min_chars=2, max_chars=100)
    accessed_at = factory.Faker("date")
    zohoimage_set = factory.RelatedFactoryList(
        factory="tests.products.factories.ZohoImageFactory",
        factory_related_name="zohoimage_set",
        size=0,
    )


class ZohoImageFactory(BaseModelFactory):
    """Factory for testing ZohoImage model."""

    class Meta:
        model = ZohoImage
        django_get_or_create = ("zoho_record",)

    id = factory.Faker("random_int", min=100, max=9223372036854775807)
    zoho_record = factory.SubFactory(factory=ZohoModuleRecordFactory)
    image = factory.django.ImageField(color=factory.Faker("color"))
