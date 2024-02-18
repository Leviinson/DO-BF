from django.db import models


# Create your models here.
def user_directory_path(
    obj: "AboutUsContextModel",
    filename: str,
) -> str:
    """Define path for added images."""
    return "{0}/{1}".format(obj.__class__.__name__.lower(), filename)


class AboutUsContextModel(models.Model):
    main_image_upper = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Первая большая картинка",
        null=True,
    )
    main_image_down = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Вторая большая картинка",
        null=True,
    )
    small_image_left_first = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Первая картинка левого столбика",
        null=True,
    )
    small_image_right_first = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Первая картинка правого столбика",
        null=True,
    )
    small_image_left_second = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Вторая картинка левого столбика",
        null=True,
    )
    small_image_right_second = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Вторая картинка правого столбика",
        null=True,
    )
    small_image_left_third = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Третья картинка левого столбика",
        null=True,
    )
    small_image_right_third = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Третья картинка правого столбика",
        null=True,
    )


class DeliveryDataModel(models.Model):
    main_image = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Первая большая картинка",
        null=True,
    )


class ContactsDataModel(models.Model):
    main_image = models.ImageField(
        upload_to=user_directory_path,
        verbose_name="Первая большая картинка",
        null=True,
    )
