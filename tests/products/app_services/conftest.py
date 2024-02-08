"""Pytest fixtures for 'products.app_services' module."""
from typing import Dict, List, Tuple

import pytest
from faker import Faker


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


def compare_dict(expected_list: List[Dict], result_list: List[Dict], i: int, j: int) -> None:
    """Compare two dicts from different list."""
    for key, value in expected_list[i].items():
        if key != "id":
            assert result_list[j][key] == value


@pytest.fixture
def create_single_product_fake_data(faker: Faker) -> Tuple[Dict, Dict]:
    """Create single product fake data."""
    input_dict: Dict = dict()
    formatted_dict: Dict = dict()
    formatted_dict["country_name"] = faker.country()
    input_dict["region_id.country_id.Name"] = formatted_dict["country_name"]
    formatted_dict["region_name"] = faker.city()
    input_dict["region_id.city"] = formatted_dict["region_name"]
    formatted_dict["subcategory_name"] = faker.pystr(min_chars=3, max_chars=100)
    input_dict["subcategory_id.Name"] = formatted_dict["subcategory_name"]
    formatted_dict["category_name"] = faker.pystr(min_chars=3, max_chars=100)
    input_dict["subcategory_id.category_id.Name"] = formatted_dict["category_name"]
    formatted_dict["Name"] = faker.pystr(min_chars=3, max_chars=100)
    input_dict["Name"] = formatted_dict["Name"]
    formatted_dict["unit_price"] = faker.random_int(min=10, max=100000)
    input_dict["unit_price"] = formatted_dict["unit_price"]
    formatted_dict["discount"] = faker.random_int(max=95)
    input_dict["discount"] = formatted_dict["discount"]
    formatted_dict["discount_start_date"] = faker.date()
    input_dict["discount_start_date"] = formatted_dict["discount_start_date"]
    formatted_dict["discount_end_date"] = faker.date()
    input_dict["discount_end_date"] = formatted_dict["discount_end_date"]
    formatted_dict["desc"] = faker.pystr(min_chars=3, max_chars=400)
    input_dict["desc"] = formatted_dict["desc"]
    formatted_dict["spec"] = faker.pystr(min_chars=3, max_chars=400)
    input_dict["spec"] = formatted_dict["spec"]
    formatted_dict["is_bouquet"] = faker.pybool()
    input_dict["is_bouquet"] = formatted_dict["is_bouquet"]
    return input_dict, formatted_dict


@pytest.fixture
def create_single_product_fake_bouquet_data(faker: Faker) -> Tuple[List[Dict], Dict]:
    """Create single product fake bouquet data."""
    input_list: List = []
    formatted_dict: Dict = dict()
    flowers = [faker.pystr(min_chars=3, max_chars=10) for _ in range(4)]
    colors = [faker.color_name() for _ in range(4)]
    amount_of_flowers = faker.random_int(min=1, max=50)
    formatted_dict["bouquet_flowers"] = flowers
    formatted_dict["bouquet_colors"] = colors
    formatted_dict["bouquet_flowers_amount"] = amount_of_flowers
    formatted_dict["bouquets_sizes"] = []
    for _ in range(faker.random_int(min=5, max=10)):
        price: int = faker.random_int(min=10, max=10000)
        value: int = faker.pystr(min_chars=1, max_chars=10)
        input_list.append(
            {
                "bouquet_id.flowers": flowers,
                "bouquet_id.amount_of_flowers": amount_of_flowers,
                "bouquet_id.colors": colors,
                "price": price,
                "value": value,
                "id": faker.random_int(min=10000000, max=100000000),
            }
        )
        formatted_dict["bouquets_sizes"].append({"price": price, "value": value})
    return input_list, formatted_dict


@pytest.fixture
def create_fake_products(faker: Faker) -> List[Dict]:
    """Create fake products list."""
    result: List = []
    for _ in range(9):
        result.append(
            {
                "Name": faker.pystr(min_chars=2, max_chars=100),
                "unit_price": faker.random_int(min=10, max=10000),
                "discount": faker.random_int(min=2, max=100),
                "discount_start_date": faker.date(),
                "discount_end_date": faker.date(),
                "slug": faker.slug(),
                "is_recommended": faker.pybool(),
                "is_bouquet": faker.pybool(),
            }
        )
    return result


@pytest.fixture
def create_fake_products_bouquets(faker: Faker) -> Tuple[List[Dict], List[Dict]]:
    """Create fake lists of bouquets data dict."""
    bouquets: List = []
    formatted_bouquets: List = []
    for _ in range(faker.random_int(min=10, max=20)):
        name: str = faker.pystr(min_chars=2, max_chars=100)
        unit_price: int = faker.random_int(min=10, max=10000)
        discount: int = faker.random_int(min=2, max=100)
        discount_start_date: str = faker.date()
        discount_end_date: str = faker.date()
        slug: str = faker.slug()
        is_recommended: bool = faker.pybool()
        is_bouquet: bool = True
        flowers: List[str] = [faker.color_name() for _ in range(5)]
        colors: List[str] = [faker.color_name() for _ in range(5)]
        bouquets.append(
            {
                "product_id.Name": name,
                "product_id.unit_price": unit_price,
                "product_id.discount": discount,
                "product_id.discount_start_date": discount_start_date,
                "product_id.discount_end_date": discount_end_date,
                "product_id.slug": slug,
                "product_id.is_recommended": is_recommended,
                "product_id.is_bouquet": is_bouquet,
                "flowers": flowers,
                "colors": colors,
                "product_id.id": faker.random_int(min=100000000, max=10000000000),
                "color": None,
                "flower": None,
            }
        )
        formatted_bouquets.append(
            {
                "Name": name,
                "unit_price": unit_price,
                "discount": discount,
                "discount_start_date": discount_start_date,
                "discount_end_date": discount_end_date,
                "slug": slug,
                "is_recommended": is_recommended,
                "is_bouquet": is_bouquet,
                "flowers": flowers,
                "colors": colors,
                "id": faker.random_int(min=100000000, max=10000000000),
            }
        )
    return bouquets, formatted_bouquets


@pytest.fixture
def get_fake_id_images_response_and_test_data(
    faker: Faker,
) -> Tuple[List[Tuple[int, str]], Dict]:
    """Get fake custom_record_operations.get_record response and input data."""
    response_dict: Dict = {"id": faker.random_int(min=10000, max=1000000), "images": []}
    input_list: List = []
    number = faker.random_int(min=3, max=10)
    for _ in range(number):
        image_id: int = faker.random_int(min=100000000, max=10000000000)
        file_name: str = faker.pystr(min_chars=10, max_chars=100)
        input_list.append((image_id, file_name))
        response_dict["images"].append(Image(image_id, file_name))
    return input_list, response_dict
