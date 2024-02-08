"""Base models for testing section."""

import random
import typing

import factory
from django.db import models


class BaseModelFactory(factory.django.DjangoModelFactory):
    """Class for adding checking functionality to instances and subclasses."""

    class Meta:
        abstract = True

    @staticmethod
    def check_factory(
        factory_class: typing.Type["BaseModelFactory"],
        model: typing.Type[models.Model],
    ) -> None:
        """Test that factory created successfully."""
        obj = factory_class()
        size = random.randint(2, 3)
        objs = factory_class.create_batch(size=size)

        assert isinstance(obj, model)
        assert size == len(objs)
        for i in objs:
            assert isinstance(obj, model)
