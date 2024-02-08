"""Fixtures for testing services module."""
from copy import deepcopy
from typing import Dict, List, Tuple

import pytest
from django.http import HttpRequest
from django.utils.functional import cached_property
from django.utils.text import slugify
from faker import Faker

from mainpage.models import Contact
from tests.mainpage.factories import ContactFactory


class Image:
    """Class repeat ImageUpload object functionality."""

    def __init__(self, image_id: int, filename: str) -> None:
        """Create instance attributes."""
        self.id: int = image_id
        self.filename: str = filename

    def get_id(self) -> int:
        """Get self id."""
        return self.id

    def get_file_name(self) -> str:
        """Get self filename."""
        return self.filename


class ModHttpRequest(HttpRequest):
    """Modified HttpRequest class for testing."""

    def __init__(self, headers) -> None:
        """Rewrite init method, add variable."""
        super().__init__()
        self.variable = headers

    @cached_property
    def headers(self):
        """Get headers attribute."""
        return self.variable


@pytest.fixture
def get_fake_region_products(faker: Faker) -> List[Dict]:
    """Create fake product list for testing fetch_region_products."""
    input_list: List = []
    for _ in range(faker.random_int(min=10, max=30)):
        product = faker.pystr(min_chars=2, max_chars=40)
        input_list.append(
            {
                "id": faker.random_int(min=9999999999, max=1000000000000),
                "Name": product,
                "unit_price": faker.random_int(min=10, max=10000),
                "discount": faker.pyfloat(min_value=0, max_value=100),
                "discount_start_date": faker.date_time(),
                "region_id.slug": slugify(faker.city()),
                "discount_end_date": faker.date_time(),
                "slug": slugify(product),
                "is_recommended": faker.pybool(),
                "is_bouquet": faker.pybool(),
                "subcategory_id.Name": faker.pystr(min_chars=2, max_chars=40),
                "subcategory_id.slug": faker.pystr(min_chars=3, max_chars=40),
            }
        )
    return input_list


@pytest.fixture
def get_fake_currency_list(faker: Faker) -> List[Dict[str, int]]:
    """Create fake currency list for testing fetch_currency_list."""
    input_list: List = []
    for _ in range(faker.random_int(min=2, max=5)):
        currency_symbol, currency_name = faker.currency()
        input_list.append(
            {
                "id": faker.random_int(min=999999999999, max=1000000000000),
                "Name": currency_name,
                "symbol": currency_symbol,
                "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
            }
        )
    return input_list


@pytest.fixture
def get_faker_regions(faker: Faker) -> Tuple[List[Dict[str, int]], Dict[str, str]]:
    """Create input list and output dict for fetch_region testing."""
    input_list: List = []
    output_dict: Dict = dict()
    for _ in range(faker.random_int(min=10, max=30)):
        country = faker.country()
        input_list.append(
            {
                "id": str(faker.random_int(min=999999999999, max=1000000000000)),
                "code": country,
                "slug": slugify(country),
            }
        )
        output_dict[country] = slugify(country)
    return input_list, output_dict


@pytest.fixture
def get_faker_countries(faker: Faker) -> Tuple[List[Dict[str, int]], Dict]:
    """Create input list and result dict for fetch_countries testing."""
    input_list: List = []
    output_dict: Dict = dict()
    for _ in range(faker.random_int(min=10, max=30)):
        country = faker.country()
        input_list.append(
            {
                "id": faker.random_int(min=999999999999, max=1000000000000),
                "code": country,
            }
        )
        output_dict[country] = None
    return input_list, output_dict


@pytest.fixture
def get_fake_meta_headers(faker: Faker) -> HttpRequest:
    """Create fake header for testing get_client_ip."""
    ip: str = faker.ipv4()
    request: HttpRequest = HttpRequest()
    request.META["HTTP_X_FORWARDED_FOR"] = "abc,ade,ert," + ip
    request.META["HTTP_X_REAL_IP"] = ip
    request.META["REMOTE_ADDR"] = ip
    return request


@pytest.fixture
def get_fake_location_data(faker: Faker) -> Dict:
    """Create fake location data."""
    return {
        "ip": faker.ipv4(),
        "city": faker.city(),
        "region": faker.city(),
        "country": faker.country(),
    }


@pytest.fixture
@pytest.mark.django_db
def get_regions_data(faker: Faker) -> Tuple[List[Dict], List[Dict]]:
    """Create fake regions data."""
    input_list: List = []
    for _ in range(faker.random_int(min=5, max=7)):
        input_list.append(
            {
                "id": faker.random_int(min=1),
                "slug": faker.slug(),
                "Name": faker.pystr(min_chars=1),
                "country_id.currency_id.Name": faker.currency_code(),
                "country_id.code": faker.country(),
                "country_id.Name": faker.country(),
                "local_phone_number_1": faker.phone_number(),
                "local_phone_number_2": faker.phone_number(),
                "telegram_link": faker.email(),
                "viber_link": faker.email(),
                "whatsapp_link": faker.email(),
                "facebook_link": faker.email(),
                "instagram_link": faker.email(),
                "Email": faker.email(),
            }
        )
    output_list: List = deepcopy(input_list)
    contact: Contact = ContactFactory()
    for item in output_list:
        item["city"] = item.pop("Name")
        item["default_currency"] = item.pop("country_id.currency_id.Name")
        item["email"] = item.pop("Email")
        item["country_code"] = item.pop("country_id.code")
        item["international_phone_number"] = contact.international_phone_number
        item["country_name"] = item.pop("country_id.Name")
    return input_list, output_list


@pytest.fixture
def get_fake_products_data_with_images(faker: Faker) -> Tuple[List[Dict], List[Dict]]:
    """Get fake products data with images for testing embed_products_image."""
    products: List = []
    output_products: List = []
    for _ in range(5):
        slug: str = slugify(faker.pystr(min_chars=3))
        product_id: str = str(faker.random_int(min=1000, max=10000000))
        products.append({"id": product_id, "slug": slug})
        images: List = []
        for _ in range(3):
            images.append(Image(faker.random_int(min=1000, max=10000000), faker.file_name()))
        output_products.append({"id": product_id, "slug": slug, "images": images})
    return products, output_products
