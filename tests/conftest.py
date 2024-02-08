"""Pytest fixtures for 'API' project."""

import random
from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, Tuple

import pytest
from django.utils.text import slugify
from faker import Faker


@pytest.fixture(scope="function", autouse=True)
def faker_seed() -> None:
    """Generate random seed for Faker instance."""
    return random.seed(version=3)


#   TODO Check for usage in tests
@pytest.fixture
def get_response_categories_list(faker: Faker) -> Tuple[List[Dict], List[Dict]]:
    """Create dict for emulating Zoho CRM categories list."""
    input_list: List = []
    output_list: List = []
    for _ in range(faker.random_int(min=5, max=10)):
        category = faker.pystr(min_chars=4, max_chars=100)
        subcategories: List = []
        for i in range(faker.random_int(min=5, max=10)):
            subcategory = faker.pystr(min_chars=1, max_chars=100)
            input_list.append(
                {
                    "category_id.Name": category,
                    "Name": subcategory,
                    "slug": slugify(subcategory),
                }
            )
            subcategories.append({"Name": subcategory, "slug": slugify(subcategory)})
        output_list.append({"Name": category, "subcategories": subcategories})
    return input_list, output_list


@pytest.fixture
def get_response_subcategories_list(faker: Faker) -> Tuple[List, List]:
    """Create lists for emulating Zoho CRM subcategories list."""
    input_list: List = []
    for _ in range(faker.random_int(min=6, max=10)):
        input_list.append(
            {
                "id": str(faker.random_int(min=1)),
                "category_id.Name": faker.pystr(min_chars=1),
                "category_id.slug": faker.slug(),
                "category_id.id": faker.random_int(min=1),
                "Name": faker.pystr(min_chars=1),
                "slug": faker.slug(),
            }
        )
    output_list: List = deepcopy(input_list)
    for item in output_list:
        item["category_id"] = item.pop("category_id.id")
        item["category_slug"] = item.pop("category_id.slug")
        item["category_name"] = item.pop("category_id.Name")
    return input_list, output_list


@pytest.fixture
def get_response_format_categories_and_related_subcategories(
    get_response_subcategories_list: Tuple[List, List]
):
    """Create lists for emulating Zoho CRM categories and subcategories data."""
    input_list, output_list = get_response_subcategories_list
    categories_list: List = []
    categories_and_subcategories: List = []
    help_dict: defaultdict = defaultdict(list)
    for item in output_list:
        help_dict[item["category_slug"]].append(item)
    for item in help_dict.values():
        if item:
            categories_and_subcategories.append(
                {
                    "id": item[0]["category_id"],
                    "Name": item[0]["category_name"],
                    "slug": item[0]["category_slug"],
                    "subcategories": item,
                }
            )
            categories_list.append(
                {
                    "id": item[0]["category_id"],
                    "Name": item[0]["category_name"],
                    "slug": item[0]["category_slug"],
                }
            )
    return categories_list, categories_and_subcategories


@pytest.fixture
def get_fake_bouquet_sizes(faker: Faker) -> Tuple[List[Dict], Dict]:
    """Get fake bouquet sizes data."""
    input_list: List = []
    bouquet_sizes: List = []
    flowers = faker.pylist(value_types=[str])
    amount = faker.random_int(min=1)
    colors = faker.pylist(value_types=[str])
    for _ in range(4):
        value = faker.random_int(min=1)
        price = faker.pyfloat(min_value=1)
        input_list.append(
            {
                "value": value,
                "price": price,
                "bouquet_id.flowers": flowers,
                "bouquet_id.amount_of_flowers": amount,
                "bouquet_id.colors": colors,
            }
        )
        bouquet_sizes.append(
            {
                "value": value,
                "price": price,
            }
        )
    output_dict: Dict = {
        "bouquet_flowers": flowers,
        "bouquet_flowers_amount": amount,
        "bouquet_colors": colors,
        "bouquet_sizes": bouquet_sizes,
    }
    return input_list, output_dict


def compare_dicts(first: Dict, second: Dict) -> None:
    """Compare two dicts for equality."""
    for key, value in first.items():
        assert second[key] == value


def compare_lists_dicts(first: List[Dict], second: List[Dict]) -> None:
    """Compare two lists with dicts for equality."""
    for i, item in enumerate(first):
        compare_dicts(item, second[i])
