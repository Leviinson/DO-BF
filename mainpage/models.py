"""Models list for 'mainpage' app."""

from __future__ import annotations

from django.db import models


def user_directory_path(
    obj: SeoBlock,
    filename: str,
) -> str:
    """Define path for added images."""
    return "{0}/{1}".format(obj.__class__.__name__.lower(), filename)


class Contact(models.Model):
    """Model for contact info."""

    international_phone_number = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Телефонный номер 1 международного оператора",
    )

    def __str__(self) -> str:
        """Represent class."""
        return "Contacts info"


class SeoBlock(models.Model):
    """Model for SEO blocks."""

    description = models.CharField(
        max_length=255,
        verbose_name="Подпись",
    )
    picture = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Картинка",
        null=True,
    )
    button = models.CharField(
        max_length=50,
        verbose_name="Подпись кнопки",
    )
    link = models.CharField(
        max_length=255,
        verbose_name="Ссылка",
    )

    def __str__(self) -> str:
        """Represent class."""
        return str(self.description)


class MainSlider(models.Model):
    """Model for main slider."""

    ORDINAL_NUMBERS = ((1, "1"), (2, "2"), (3, "3"), (4, "4"))
    description_up = models.CharField(
        max_length=255,
        verbose_name="Подпись верхняя",
    )
    description_down = models.CharField(
        max_length=255,
        verbose_name="Подпись нижняя",
    )
    picture = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Картинка",
        null=True,
    )
    button = models.CharField(
        max_length=50,
        verbose_name="Подпись кнопки",
    )
    link = models.CharField(max_length=15, verbose_name="Ссылка кнопки", default="", blank=True)
    ordinal_number = models.IntegerField(
        choices=ORDINAL_NUMBERS,
        unique=True,
    )

    def __str__(self) -> str:
        """Represent model."""
        return f"{self.button}"


class CustomCategories(models.Model):
    """Model of the filler-categories."""

    ORDINAL_NUMBERS = ((1, "1"), (2, "2"), (3, "3"), (4, "4"))
    title = models.CharField(
        max_length=15,
        verbose_name="Название",
    )
    link = models.URLField(verbose_name="Полный адресс ссылки")
    ordinal_number = models.IntegerField(
        choices=ORDINAL_NUMBERS,
        unique=True,
    )

    def __str__(self) -> str:
        """Display category title as str()."""
        return f"{self.title}"
