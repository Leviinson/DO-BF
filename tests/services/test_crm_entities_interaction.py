"""Classes for testing services.crm_entities_interaction."""
from typing import Dict, List, Tuple
from unittest.mock import MagicMock, patch

from django.utils.text import slugify
from faker import Faker

from config.constants import Constants
from services.crm_entities_interaction import region_handler, zoho_data


class TestFetchRegions:
    """Class for testing zoho_data.fetch_regions."""

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_regions(
        self, get_mock: MagicMock, get_faker_regions: List[Dict[str, str]]
    ) -> None:
        """Test zoho_data.fetched_regions."""
        input_list, expected_result = get_faker_regions
        get_mock.return_value = {"data": input_list, "info": {"more_records": False}}
        result: Dict = zoho_data.fetch_regions()
        for key in expected_result.keys():
            assert expected_result[key] == result[key]
        assert result[Constants.DEFAULT_REGION] == slugify(Constants.DEFAULT_REGION)

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_regions_many(
        self, get_mock: MagicMock, get_faker_regions: List[Dict[str, str]]
    ) -> None:
        """Test zoho_data.fetched_regions."""
        input_list, expected_result = get_faker_regions
        get_mock.side_effect = [
            {"data": input_list[:5], "info": {"more_records": True}},
            {"data": input_list[5:], "info": {"more_records": False}},
        ]
        result: Dict = zoho_data.fetch_regions()
        for key in expected_result.keys():
            assert expected_result[key] == result[key]
        assert result[Constants.DEFAULT_REGION] == slugify(Constants.DEFAULT_REGION)

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_regions_empty(
        self, get_mock: MagicMock, get_faker_regions: List[Dict[str, str]]
    ) -> None:
        """Test zoho_data.fetched_regions. Empty result."""
        get_mock.return_value = dict()
        result: Dict = zoho_data.fetch_regions()
        assert isinstance(result, Dict)
        assert len(result) == 1
        assert result[Constants.DEFAULT_REGION] == slugify(Constants.DEFAULT_REGION)


class TestFetchCountries:
    """Class for testing zoho_data.fetch_countries."""

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_countries(
        self,
        get_mock: MagicMock,
        get_faker_countries: Tuple[List[Dict[str, int]], Dict],
    ) -> None:
        """Test zoho_data.fetch_countries."""
        input_list, expected_result = get_faker_countries
        get_mock.return_value = {"data": input_list, "info": {"more_records": False}}
        result: Dict = zoho_data.fetch_countries()
        for key in expected_result.keys():
            assert key in result
            assert not result[key]

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_countries_empty(
        self,
        get_mock: MagicMock,
    ) -> None:
        """Test zoho_data.fetch_countries. Empty result."""
        get_mock.return_value = dict()
        result: Dict = zoho_data.fetch_countries()
        print(result, "empty")
        assert isinstance(result, Dict)
        assert not result


class TestFetchRegionByCountryName:
    """Class for testing zoho_data.fetch_region_by_country_name."""

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_region_by_country_name(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test zoho_data.fetch_region_by_country_name."""
        region: str = faker.country()
        region_id: int = faker.random_int(min=999999999999, max=100000000000000)
        get_mock.return_value = {
            "data": [{"code": region, "id": region_id}],
            "info": {"more_records": False},
        }
        result: List = zoho_data.fetch_region_by_country_name("any_country")
        assert result[0].get("code") == region
        assert result[0].get("id") == region_id

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_region_by_country_name_empty(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test zoho_data.fetch_region_by_country_name. Empty result."""
        get_mock.return_value = dict()
        result: List = zoho_data.fetch_region_by_country_name("any_country")
        assert not result


class TestFetchCurrencyList:
    """Class for testing zoho_data.fetch_currency_list."""

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_currency_list(
        self, get_mock: MagicMock, get_fake_currency_list: List[Dict[str, int]]
    ) -> None:
        """Test zoho_fetched_data.fetch_currency_list."""
        input_list: List = get_fake_currency_list
        get_mock.return_value = {"data": input_list, "info": {"more_records": False}}
        result: List = zoho_data.fetch_currency_list()
        for i, item in enumerate(input_list):
            assert item.get("id") == result[i].get("id")
            assert item.get("Name") == result[i].get("Name")
            assert item.get("symbol") == result[i].get("symbol")

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_currency_list_constants(
        self,
        get_mock: MagicMock,
    ) -> None:
        """Test zoho_data.zoho_currency_list. Error Zoho connection."""
        get_mock.return_value = dict()
        result: List = zoho_data.fetch_currency_list()
        for i, item in enumerate(Constants.DEFAULT_CURRENCY_LIST):
            assert item.get("Name") == result[i].get("Name")
            assert item.get("symbol") == result[i].get("symbol")


class TestFetchCategoriesAndSubcategories:
    """Class for testing zoho_data.fetch_categories_and_subcategories."""

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_categories_and_subcategories(
        self,
        get_mock: MagicMock,
        get_response_categories_list: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """Test fetch_categories_and_subcategories."""
        input_list, expected_result = get_response_categories_list
        get_mock.return_value = {"data": input_list, "info": {"more_records": False}}
        result: List = zoho_data.fetch_categories_and_subcategories()
        for i, item in enumerate(result):
            assert item.get("Name") == expected_result[i].get("Name")
            for j, elem in enumerate(item.get("subcategories")):
                assert elem.get("Name") == expected_result[i].get("subcategories")[j].get(
                    "Name"
                )
                assert elem.get("slug") == expected_result[i].get("subcategories")[j].get(
                    "slug"
                )

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_categories_and_subcategories_many(
        self,
        get_mock: MagicMock,
        get_response_categories_list: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """Test fetch_categories_and_subcategories."""
        input_list, expected_result = get_response_categories_list
        get_mock.side_effect = [
            {"data": input_list[:10], "info": {"more_records": True}},
            {"data": input_list[10:], "info": {"more_records": False}},
        ]
        result: List = zoho_data.fetch_categories_and_subcategories()
        for i, item in enumerate(result):
            assert item.get("Name") == expected_result[i].get("Name")
            for j, elem in enumerate(item.get("subcategories")):
                assert elem.get("Name") == expected_result[i].get("subcategories")[j].get(
                    "Name"
                )
                assert elem.get("slug") == expected_result[i].get("subcategories")[j].get(
                    "slug"
                )

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_categories_and_subcategories_empty(
        self,
        get_mock: MagicMock,
    ) -> None:
        """Test fetch_categories_and_subcategories."""
        get_mock.return_value = dict()
        result: List = zoho_data.fetch_categories_and_subcategories()
        assert isinstance(result, List)
        assert not result


class TestFetchRegionProducts:  # TODO test with image_handler in action
    """Class for testing region_handler.fetch_region_products."""

    @patch("services.image_handlers.image_handlers.embed_products_image")
    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_region_products(
        self,
        get_mock_query: MagicMock,
        get_mock_image: MagicMock,
        get_fake_region_products: List[Dict],
        faker: Faker,
    ) -> None:
        """Test region_handler.fetch_region_products."""
        region: str = faker.country()
        input_list: List = get_fake_region_products
        get_mock_query.return_value = {"data": input_list, "info": {"more_records": False}}
        get_mock_image.side_effect = lambda x: x
        result: List[Dict] = region_handler.fetch_region_products(region)
        for i, item in enumerate(input_list):
            assert item.get("Name") == result[i].get("Name")
            assert item.get("unit_price") == result[i].get("unit_price")
            assert item.get("discount") == result[i].get("discount")
            assert item.get("discount_end_date") == result[i].get("discount_end_date")
            assert item.get("discount_start_date") == result[i].get("discount_start_date")
            assert item.get("slug") == result[i].get("slug")
            assert item.get("is_recommended") == result[i].get("is_recommended")
            assert item.get("is_bouquet") == result[i].get("is_bouquet")
            assert item.get("category_type_id.Name") == result[i].get("category_type_id.Name")

    @patch("services.image_handlers.image_handlers.embed_products_image")
    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_region_products_many(
        self,
        get_mock_query: MagicMock,
        get_mock_image: MagicMock,
        get_fake_region_products: List[Dict],
        faker: Faker,
    ) -> None:
        """Test region_handler.fetch_region_products. Two Zoho crm requests."""
        region: str = faker.country()
        input_list: List = get_fake_region_products
        get_mock_query.side_effect = [
            {"data": input_list[:5], "info": {"more_records": True}},
            {"data": input_list[5:], "info": {"more_records": False}},
        ]
        get_mock_image.side_effect = lambda x: x
        result: List[Dict] = region_handler.fetch_region_products(region)
        for i, item in enumerate(input_list):
            assert item.get("Name") == result[i].get("Name")
            assert item.get("unit_price") == result[i].get("unit_price")
            assert item.get("discount") == result[i].get("discount")
            assert item.get("discount_end_date") == result[i].get("discount_end_date")
            assert item.get("discount_start_date") == result[i].get("discount_start_date")
            assert item.get("slug") == result[i].get("slug")
            assert item.get("is_recommended") == result[i].get("is_recommended")
            assert item.get("is_bouquet") == result[i].get("is_bouquet")
            assert item.get("category_type_id.Name") == result[i].get("category_type_id.Name")

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_region_products_empty(
        self,
        get_mock: MagicMock,
        get_fake_region_products: List[Dict],
        faker: Faker,
    ) -> None:
        """Test region_handler.fetch_region_products. Empty result."""
        region: str = faker.country()
        get_mock.return_value = dict()
        result: List = region_handler.fetch_region_products(region)
        assert not result


class TestFetchRegionBouquets:
    """Class for testing region_handler.fetch_region_bouquets."""

    pass


class TestFetchRegionBestsellers:
    """Class for testing region_handler.fetch_region_bestsellers."""

    pass


class TestSearchRegionProducts:
    """Class for testing region_handler.search_region_products."""

    pass
