"""Module for testing services.caching."""
from typing import Dict, List, Tuple
from unittest.mock import MagicMock, patch

import pytest
from django.core.cache import cache
from faker import Faker

from mainpage.models import Contact
from services.caching import caching
from tests.mainpage.factories import ContactFactory


class TestGetLocation:
    """Class for testing cache_data.get_location."""

    @patch("services.utils.ip_geo_locator.fetch_location")
    def test_get_location(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test cached_data.get_location."""
        cache.clear()
        ip: str = faker.ipv4()
        expected_key: str = faker.pystr(min_chars=3, max_chars=5)
        expected_value: str = faker.pystr(min_chars=5, max_chars=7)
        new_expected_key: str = faker.pystr(min_chars=3, max_chars=5)
        new_expected_value: str = faker.pystr(min_chars=5, max_chars=7)
        get_mock.return_value = {expected_key: expected_value}
        result: Dict = caching.get_location(ip)
        for key, value in result.items():
            assert key == expected_key
            assert value == expected_value
        get_mock.return_value = {new_expected_key: new_expected_value}
        result = caching.get_location(ip)
        for key, value in result.items():
            assert key == expected_key
            assert value == expected_value
        cache.clear()
        result = caching.get_location(ip)
        for key, value in result.items():
            assert key == new_expected_key
            assert value == new_expected_value


class TestGetRegionDict:
    """Class for testing cache_data.get_region_dict."""

    @patch("services.crm_entities_interaction.zoho_data.fetch_regions")
    def test_get_region_dict(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test cache_data.get_region_dict."""
        cache.clear()
        expected_key: str = faker.pystr(min_chars=3, max_chars=5)
        expected_value: str = faker.pystr(min_chars=5, max_chars=7)
        new_expected_key: str = faker.pystr(min_chars=3, max_chars=5)
        new_expected_value: str = faker.pystr(min_chars=5, max_chars=7)
        get_mock.return_value = {expected_key: expected_value}
        result: Dict = caching.get_region_dict()
        for key, value in result.items():
            assert key == expected_key
            assert value == expected_value
        get_mock.return_value = {new_expected_key: new_expected_value}
        result = caching.get_region_dict()
        for key, value in result.items():
            assert key == expected_key
            assert value == expected_value
        cache.clear()
        result = caching.get_region_dict()
        for key, value in result.items():
            assert key == new_expected_key
            assert value == new_expected_value


class TestGetRegionSlugDict:
    """Class for testing cache_data.get_region_slug_dict."""

    @patch("services.caching.caching.get_region_dict")
    def test_get_region_slug_dict(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test cache_data.get_region_slug_dict."""
        cache.clear()
        input_dict: Dict = dict()
        new_input_dict: Dict = dict()
        for _ in range(faker.random_int(min=10, max=50)):
            input_dict[faker.pystr(min_chars=20, max_chars=40)] = faker.pystr(
                min_chars=1, max_chars=20
            )
            new_input_dict[faker.pystr(min_chars=20, max_chars=40)] = faker.pystr(
                min_chars=1, max_chars=20
            )
        get_mock.return_value = input_dict
        result: Dict = caching.get_region_slug_dict()
        for key, value in result.items():
            assert value in input_dict
            assert input_dict[value] == key
        get_mock.return_value = new_input_dict
        result: Dict = caching.get_region_slug_dict()
        for key, value in result.items():
            assert value in input_dict
            assert input_dict[value] == key
        cache.clear()
        result: Dict = caching.get_region_slug_dict()
        for key, value in result.items():
            assert value in new_input_dict
            assert new_input_dict[value] == key


class TestGetCountryDict:
    """Class for testing cache_data.get_country_dict."""

    @patch("services.crm_entities_interaction.zoho_data.fetch_countries")
    def test_get_country_dict(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test cache_data.get_country_dict."""
        expected_countries: Dict = dict()
        new_expected_countries: Dict = dict()
        for _ in range(faker.random_int(min=10, max=50)):
            expected_countries[faker.country()] = None
            new_expected_countries[faker.country()] = None
        get_mock.return_value = expected_countries
        result: Dict = caching.get_country_dict()
        for key, value in result.items():
            assert key in expected_countries
            assert not value
            assert not expected_countries[key]
        get_mock.return_value = new_expected_countries
        result: Dict = caching.get_country_dict()
        for key, value in result.items():
            assert key in expected_countries
            assert not value
            assert not expected_countries[key]
        cache.clear()
        result: Dict = caching.get_country_dict()
        for key, value in result.items():
            assert key in new_expected_countries
            assert not value
            assert not new_expected_countries[key]


class TestSetCountryDict:
    """Class for testing cache_data.set_country_dict."""

    def test_set_country_dict(
        self,
        faker: Faker,
    ) -> None:
        """Test cache_data.set_country_dict."""
        cache.clear()
        expected_countries: Dict = dict()
        for _ in range(faker.random_int(min=10, max=50)):
            expected_countries[faker.country()] = None
        caching.set_country_dict(expected_countries)
        result = cache.get("country_dict")
        for key, value in result.items():
            assert key in expected_countries
            assert not value
            assert not expected_countries[key]
        assert len(expected_countries) == len(result)
        cache.clear()
        assert not cache.get("country_dict")


class TestGetRegionProducts:
    """Class for testing cache_data.get_region_products."""

    @patch("services.caching.caching.get_categories_ids_slug_dict")
    @patch("services.crm_entities_interaction.region_handler.fetch_region_products")
    def test_get_region_products(
        self,
        get_mock: MagicMock,
        get_mock_ids: MagicMock,
        faker: Faker,
        get_fake_region_products: List,
    ) -> None:
        """Test cache_data.get_region_products."""
        cache.clear()
        input_list: List = get_fake_region_products
        new_input_list: List = []
        region: str = faker.country()
        get_mock.return_value = input_list
        get_mock_ids.return_value = {
            item["subcategory_id.category_id"]["id"]: "category" for item in input_list
        }
        result: List = caching.get_region_products(region)
        for i, elem in enumerate(result):
            for key, value in elem.items():
                assert input_list[i][key] == value
        get_mock.return_value = new_input_list
        result: List = caching.get_region_products(region)
        for i, elem in enumerate(result):
            for key, value in elem.items():
                assert input_list[i][key] == value
        cache.clear()
        result: List = caching.get_region_products(region)
        assert isinstance(result, List)
        assert not result


class TestGetCurrencyList:
    """Class for testing cache_data.get_currency_list."""

    @patch("services.crm_entities_interaction.zoho_data.fetch_currency_list")
    def test_get_currency_list(
        self,
        get_mock: MagicMock,
        faker: Faker,
        get_fake_currency_list: List[Dict],
    ) -> None:
        """Test cache_data.get_currency_list."""
        input_list: List = get_fake_currency_list
        new_input_list: List = []
        for _ in range(faker.random_int(min=10, max=15)):
            currency_symbol, currency_name = faker.currency()
            new_input_list.append(
                {
                    "id": faker.random_int(min=9999999999, max=1000000000000),
                    "Name": currency_name,
                    "symbol": currency_symbol,
                }
            )
        get_mock.return_value = input_list
        result: List = caching.get_currency_list()
        for i, item in enumerate(result):
            for key, value in item.items():
                assert input_list[i][key] == value
        get_mock.return_value = new_input_list
        result: List = caching.get_currency_list()
        for i, item in enumerate(result):
            for key, value in item.items():
                assert input_list[i][key] == value
        cache.clear()
        result: List = caching.get_currency_list()
        for i, item in enumerate(result):
            for key, value in item.items():
                assert new_input_list[i][key] == value


class TestGetRegionBouquets:
    """Class for testing cache_data.get_region_bouquets."""

    @patch("services.caching.caching.get_region_products")
    def test_get_region_bouquets(
        self,
        get_mock: MagicMock,
        faker: Faker,
        get_fake_region_products: List[Dict],
    ) -> None:
        """Test cache_data.get_region_bouquets."""
        region: str = faker.city()
        region_products: List[Dict] = get_fake_region_products
        get_mock.return_value = region_products
        expected_result: List[Dict] = list(
            filter(lambda x: x.get("is_bouquet"), region_products)
        )
        result = caching.get_region_bouquets(region)
        for i, item in enumerate(result):
            for key, value in item.items():
                assert expected_result[i][key] == value


class TestGetCategoriesAndSubcategories:
    """Class for testing cache_data.get_categories_and_subcategories."""

    @patch("services.crm_entities_interaction.zoho_data.fetch_categories_and_subcategories")
    def test_get_categories_and_subcategories(
        self,
        get_mock: MagicMock,
        get_response_categories_list: Tuple[List[Dict], List[Dict]],
        faker: Faker,
    ) -> None:
        """Test cache_data.get_categories_and_subcategories."""
        cache.clear()
        output_categories, some_categories = get_response_categories_list
        new_output_categories: List = [{faker.country(): faker.city()} for _ in range(3)]
        get_mock.return_value = output_categories
        result: List = caching.get_categories_and_subcategories()
        for i, elem in enumerate(result):
            for key, value in elem.items():
                assert key in output_categories[i]
                assert output_categories[i][key] == value
        get_mock.return_value = new_output_categories
        result: List = caching.get_categories_and_subcategories()
        for i, elem in enumerate(result):
            for key, value in elem.items():
                assert key in output_categories[i]
                assert output_categories[i][key] == value
        cache.clear()
        result: List = caching.get_categories_and_subcategories()
        for i, elem in enumerate(result):
            for key, value in elem.items():
                assert key in new_output_categories[i]
                assert new_output_categories[i][key] == value


@pytest.mark.django_db
class TestGetContacts:
    """Class for testing caching.get_contacts."""

    pytestmark = pytest.mark.django_db

    def test_get_contacts(self, faker: Faker) -> None:
        """Test get_contacts."""
        expected_result: Contact = ContactFactory()
        response = caching.get_contacts()
        assert expected_result == response


class TestGetCategoriesIdsSlugDict:
    """Class for testing caching.get_categories_ids_slug_dict."""

    @patch("services.crm_entities_interaction.zoho_data.fetch_categories_ids_slug_info")
    def test_get_categories_ids_slug_dict(
        self,
        get_mock: MagicMock,
        faker: Faker,
        get_fake_currency_list: List[Dict],
    ) -> None:
        """Test get_categories_ids_slug_dict."""
        input_list: List = get_fake_currency_list
        get_mock.return_value = input_list
        result: List = caching.get_categories_ids_slug_dict()
        print(input_list)
        print(result)
        for i, item in enumerate(result):
            for key, value in input_list[i].items():
                assert item[key] == value
        get_mock.return_value = input_list[1:-1]
        result = caching.get_categories_ids_slug_dict()
        for i, item in enumerate(result):
            for key, value in input_list[i].items():
                assert item[key] == value
        cache.clear()
        result = caching.get_categories_ids_slug_dict()
        for i, item in enumerate(result):
            for key, value in input_list[1:-1][i].items():
                assert item[key] == value
