"""Module for testing services mixins functionality."""
from typing import Dict, List, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from asgiref.sync import async_to_sync
from django.http import HttpRequest
from faker import Faker

from services.mixins import ApplicationMixin
from services.utils import formatters
from tests.mainpage.factories import CustomCategoriesFactory


@pytest.mark.django_db
class TestGetRegion:
    """Class for testing ApplicationMixin get_region method."""

    @pytest.mark.django_db
    def test_get_region(
        self, faker: Faker, get_regions_data: Tuple[List[Dict], List[Dict]]
    ) -> None:
        """Test get_region method."""
        input_list, regions = get_regions_data
        region: Dict = faker.random_element(elements=regions)
        result = ApplicationMixin.get_region(regions, region["slug"])
        for key, value in result.items():
            assert region[key] == value


@pytest.mark.django_db
class TestGetCommonContext:
    """Class for testing ApplicationMixin get_common_context method."""

    pytestmark = pytest.mark.django_db

    @patch("services.data_getters.crm_data.get_subcategories_list", new_callable=AsyncMock)
    @patch("services.data_getters.crm_data.get_categories_list", new_callable=AsyncMock)
    @patch("services.data_getters.crm_data.get_currency_list", new_callable=AsyncMock)
    @patch("services.data_getters.crm_data.get_regions_list", new_callable=AsyncMock)
    def test_get_common_context(
        self,
        region_mock: AsyncMock,
        currency_mock: AsyncMock,
        categories_list_mock: AsyncMock,
        sucategories_list_mock: AsyncMock,
        faker: Faker,
        get_regions_data: Tuple[List[Dict], List[Dict]],
        get_fake_currency_list: List[Dict[str, int]],
        get_response_format_categories_and_related_subcategories: Tuple[List, List],
        get_response_subcategories_list: Tuple[List, List],
    ) -> None:
        """Test get_common_context."""
        input_list, regions = get_regions_data
        categories, output = get_response_format_categories_and_related_subcategories
        input_list, subcategories = get_response_subcategories_list
        region: Dict = faker.random_element(elements=regions)
        context: Dict = {
            "region_slug": region["slug"],
        }
        currencies = get_fake_currency_list
        selected_currency = faker.random_element(elements=currencies)
        output_categories = formatters.format_categories_and_related_subcategories(
            categories, subcategories
        )

        region_mock.return_value = regions
        currency_mock.return_value = currencies
        categories_list_mock.return_value = categories
        sucategories_list_mock.return_value = subcategories

        application_mixin = ApplicationMixin()
        application_mixin.request = HttpRequest()
        application_mixin.request.session = {}
        application_mixin.request.GET = {"currency": selected_currency["Name"]}
        result = async_to_sync(application_mixin.get_common_context)(**context)
        for key, value in result["region"].items():
            assert region[key] == value
        for i, currency in enumerate(currencies):
            for key, value in result["currencies"][i].items():
                assert currency[key] == value
        for key, value in result["selected_currency"].items():
            assert selected_currency[key] == value
        for i, category in enumerate(result["categories"]):
            for key, value in output_categories[i].items():
                if key == "subcategories":
                    for j, subcategory in enumerate(category["subcategories"]):
                        for k, v in value[j].items():
                            assert subcategory[k] == v
                else:
                    assert category[key] == value
        assert result["cart_products_quantity"] == 0


@pytest.mark.django_db
class TestGetSelectedRegion:
    """Class for testing ApplicationMixin _get_selected_region."""

    pytestmark = pytest.mark.django_db

    def test_get_selected_region(
        self,
        faker: Faker,
        get_regions_data: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """Test _get_selected_region."""
        input_list, regions = get_regions_data
        region: Dict = faker.random_element(elements=regions)
        context: Dict = {
            "region_slug": region["slug"],
        }
        result = async_to_sync(ApplicationMixin()._get_selected_region)(context, regions)
        for key, value in result["region"].items():
            assert region[key] == value

    @patch("services.client_handlers.client_handler.get_client_region", new_callable=AsyncMock)
    def test_get_selected_region_empty_region_slug(
        self,
        client_region_mock: AsyncMock,
        faker: Faker,
        get_regions_data: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """Test _get_selected_region, empty context 'region_slug' key."""
        input_list, regions = get_regions_data
        context: Dict = {}
        region = faker.random_element(elements=regions)
        client_region_mock.return_value = region
        result = async_to_sync(ApplicationMixin()._get_selected_region)(context, regions)
        for key, value in result["region"].items():
            assert region[key] == value

    @patch("services.mixins.ApplicationMixin.get_region")
    @patch("services.client_handlers.client_handler.get_client_region", new_callable=AsyncMock)
    def test_get_selected_region_empty_region_slug_and_region(
        self,
        client_region_mock: AsyncMock,
        get_region_mock: MagicMock,
        faker: Faker,
        get_regions_data: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """
        Test _get_selected_region.

        Empty context 'region_slug' key and empty result of get_client_region.
        """
        input_list, regions = get_regions_data
        context: Dict = {}
        region = faker.random_element(elements=regions)
        client_region_mock.return_value = None
        get_region_mock.return_value = region
        result = async_to_sync(ApplicationMixin()._get_selected_region)(context, regions)
        for key, value in result["region"].items():
            assert region[key] == value


@pytest.mark.django_db
class TestGetSelectedCurrency:
    """Class for testing ApplicationMixin _get_selected_currency."""

    pytestmark = pytest.mark.django_db

    @patch("services.data_getters.crm_data.get_currency_list", new_callable=AsyncMock)
    def test_get_selected_currency(
        self,
        get_currency_mock: AsyncMock,
        faker: Faker,
        get_fake_currency_list: List[Dict[str, int]],
        get_regions_data: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """Test _get_selected_currency."""
        input_list, regions = get_regions_data
        currencies = get_fake_currency_list
        selected_currency = faker.random_element(elements=currencies)
        context: Dict = {}
        application_mixin = ApplicationMixin()
        application_mixin.request = HttpRequest()
        application_mixin.request.GET = {"currency": selected_currency["Name"]}
        get_currency_mock.return_value = currencies
        result = async_to_sync(application_mixin._get_selected_currency)(context, regions)
        for key, value in result["selected_currency"].items():
            assert selected_currency[key] == value

    @patch("services.data_getters.crm_data.get_currency_list", new_callable=AsyncMock)
    def test_get_selected_currency_empty_selected_currency(
        self,
        get_currency_mock: AsyncMock,
        faker: Faker,
        get_fake_currency_list: List[Dict[str, int]],
        get_regions_data: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """Test _get_selected_currency, empty select_currency key case."""
        input_list, regions = get_regions_data
        region_index = faker.random_int(max=len(regions) - 1)
        currencies = get_fake_currency_list
        selected_currency = faker.random_element(elements=currencies)
        regions[region_index]["default_currency"] = selected_currency["Name"]
        context: Dict = {"region": regions[region_index]}
        application_mixin = ApplicationMixin()
        application_mixin.request = HttpRequest()
        application_mixin.request.GET = {"currency": "abc"}
        get_currency_mock.return_value = currencies
        result = async_to_sync(application_mixin._get_selected_currency)(context, regions)
        for key, value in result["selected_currency"].items():
            assert selected_currency[key] == value


@pytest.mark.django_db
class TestGetCategories:
    """Class for testing ApplicationMixin _get_categories method."""

    pytestmark = pytest.mark.django_db

    @patch("services.data_getters.crm_data.get_subcategories_list", new_callable=AsyncMock)
    @patch("services.data_getters.crm_data.get_categories_list", new_callable=AsyncMock)
    def test_get_categories(
        self,
        categories_list_mock: AsyncMock,
        sucategories_list_mock: AsyncMock,
        faker: Faker,
        get_response_format_categories_and_related_subcategories: Tuple[List, List],
        get_response_subcategories_list: Tuple[List, List],
    ) -> None:
        """Test _get_categories method."""
        categories, output = get_response_format_categories_and_related_subcategories
        input_list, subcategories = get_response_subcategories_list
        context: Dict = {}
        output_categories = formatters.format_categories_and_related_subcategories(
            categories, subcategories
        )

        categories_list_mock.return_value = categories
        sucategories_list_mock.return_value = subcategories

        result = async_to_sync(ApplicationMixin()._get_categories)(context)
        for i, category in enumerate(output_categories):
            for key, value in result["categories"][i].items():
                if key == "subcategories":
                    for j, subcategory in enumerate(category["subcategories"]):
                        for k, v in value[j].items():
                            assert subcategory[k] == v
                else:
                    assert category[key] == value
        assert result.get("custom_categories") is None

    @patch("services.data_getters.crm_data.get_subcategories_list", new_callable=AsyncMock)
    @patch("services.data_getters.crm_data.get_categories_list", new_callable=AsyncMock)
    def test_get_categories_low_length(
        self,
        categories_list_mock: AsyncMock,
        sucategories_list_mock: AsyncMock,
        faker: Faker,
        get_response_format_categories_and_related_subcategories: Tuple[List, List],
        get_response_subcategories_list: Tuple[List, List],
    ) -> None:
        """Test _get_categories method, categories length less then 6 case."""
        categories, output = get_response_format_categories_and_related_subcategories
        input_list, subcategories = get_response_subcategories_list
        context: Dict = {}
        categories_number: int = faker.random_int(min=1, max=5)
        output_categories = formatters.format_categories_and_related_subcategories(
            categories[:categories_number], subcategories
        )
        custom_categories = CustomCategoriesFactory.create_batch(size=6)

        categories_list_mock.return_value = categories[:categories_number]
        sucategories_list_mock.return_value = subcategories

        result = async_to_sync(ApplicationMixin()._get_categories)(context)
        for i, category in enumerate(output_categories):
            for key, value in result["categories"][i].items():
                if key == "subcategories":
                    for j, subcategory in enumerate(category["subcategories"]):
                        for k, v in value[j].items():
                            assert subcategory[k] == v
                else:
                    assert category[key] == value
        for i, category in enumerate(result["custom_categories"]):
            assert category == custom_categories[i]
        assert len(result["custom_categories"]) == 6 - categories_number
