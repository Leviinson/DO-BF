import os

import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)
django.setup()

from custom_auth.models import User
from mainpage.models import Contact, SeoBlock


def create_records():
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            "root",
            None,
            "root",
            phone_number="+38063",
        )
    # Создайте записи в моделях
    if not Contact.objects.exists():
        Contact.objects.create(
            international_phone_number="0800000000",
        )
    if not SeoBlock.objects.exists():
        SeoBlock.objects.create(
            description="Элитные композиции для мероприятий",
            button="В коробках и корзинках!",
            picture="seoblock/Pasted_image.png",
            link=f"http://{os.getenv('NGINX_DOMEN')}/catalogue/dnipro/bouquets/?currency=USD",
        )
        SeoBlock.objects.create(
            description="Выполним любой индивидуальный заказ!",
            button="Попробовать",
            picture="seoblock/Pasted_image.png",
            link="",
        )


if __name__ == "__main__":
    create_records()
