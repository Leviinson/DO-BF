"""Pytest fixtures for 'mainpage/app_services' app module."""
from typing import Dict, List, Set, Tuple, Union

import pytest
from faker import Faker


@pytest.fixture
def create_criteria_input(faker: Faker) -> Tuple[Dict, List[Union[Set, int]]]:
    """Create satisfy_criteria input dict and tuple."""
    data: Dict = {
        "subcategory_name": faker.pystr(min_chars=2, max_chars=100),
        "unit_price": faker.random_int(min=100, max=1000),
        "some_value": faker.random_int(),
    }
    criteria: List = [
        {faker.pystr(min_chars=8, max_chars=40) for _ in range(10)},
        0,
        100000000,
    ]
    return data, criteria
