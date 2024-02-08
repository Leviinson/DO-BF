"""Module for testing products.app_services.crm_entities_interaction functionality."""
from typing import Dict, List, Tuple
from unittest.mock import MagicMock, patch

from faker import Faker

from products.app_services.crm_entities_interaction import product_detail_operations


class TestFetchProductDetails:
    """Class for testing crm_entities_interaction.fetch_product_details."""

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_product_details(
        self,
        get_mock: MagicMock,
        create_single_product_fake_data: Tuple[Dict, Dict],
        faker: Faker,
    ) -> None:
        """Test fetch_product_details."""
        input_dict, output_dict = create_single_product_fake_data
        get_mock.return_value = {"data": [input_dict], "info": {"more_records": False}}
        region_slug: str = faker.slug()
        response = product_detail_operations.fetch_product_details(
            region_slug, region_slug, region_slug
        )
        for key, value in response.items():
            assert output_dict[key] == value

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_product_details_empty(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test fetch_product_details, empty case."""
        get_mock.return_value = {"data": [], "info": {"more_records": False}}
        region_slug: str = faker.slug()
        response = product_detail_operations.fetch_product_details(
            region_slug, region_slug, region_slug
        )
        assert not response
        assert isinstance(response, Dict)


class TestFetchProductBouquetData:
    """Class for testing crm_entities_interaction.fetch_product_bouquet_data."""

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_product_bouquet_data(
        self,
        get_mock: MagicMock,
        create_single_product_fake_bouquet_data: Tuple[List[Dict], Dict],
        faker: Faker,
    ) -> None:
        """Test fetch_product_bouquet_data."""
        input_list, output_dict = create_single_product_fake_bouquet_data
        get_mock.return_value = {"data": input_list, "info": {"more_records": False}}
        response = product_detail_operations.fetch_product_bouquet_data(
            faker.pystr(min_chars=2, max_chars=100)
        )
        for key, value in output_dict.items():
            if key == "bouquets_sizes":
                for i, item in enumerate(value):
                    assert response.get("bouquets_sizes")[i].get("price") == item.get("price")
                    assert response.get("bouquets_sizes")[i].get("value") == item.get("value")
            else:
                assert response[key] == value

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_product_bouquet_data_empty(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test fetch_product_bouquet_data."""
        get_mock.return_value = {"data": [], "info": {"more_records": False}}
        response = product_detail_operations.fetch_product_bouquet_data(
            faker.pystr(min_chars=2, max_chars=100)
        )
        assert not response
        assert isinstance(response, dict)


class TestFetchFirstSubcategoryProducts:
    """Class for testing product_detail_operations.fetch_first_subcategory_products."""

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_first_subcategory_products(
        self,
        get_mock: MagicMock,
        create_fake_products: List[Dict],
        faker: Faker,
    ) -> None:
        """Test fetch_first_subcategory_products."""
        input_list = create_fake_products
        input_data = faker.slug()
        get_mock.return_value = {"data": input_list, "info": {"more_records": False}}
        response = product_detail_operations.fetch_first_subcategory_products(
            input_data, input_data, input_data
        )
        for i, item in enumerate(input_list):
            for key, value in item.items():
                assert response[i][key] == value

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_first_subcategory_products_empty(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test fetch_first_subcategory_products."""
        input_data = faker.slug()
        get_mock.return_value = {"data": [], "info": {"more_records": False}}
        response = product_detail_operations.fetch_first_subcategory_products(
            input_data, input_data, input_data
        )
        assert not response
        assert isinstance(response, List)


class TestFetchFirstProductBouquets:
    """Class for testing product_detail_operations.fetch_first_products_bouquets."""

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_first_products_bouquets(
        self,
        get_mock: MagicMock,
        create_fake_products_bouquets: Tuple[List[Dict], List[Dict]],
        faker: Faker,
    ) -> None:
        """Test fetch_first_product_bouquets."""
        bouquets, formatted_bouquets = create_fake_products_bouquets
        get_mock.return_value = {"data": bouquets, "info": {"more_records": False}}
        response = product_detail_operations.fetch_first_products_bouquets(
            faker.slug(), faker.slug()
        )
        for i, bouquet in enumerate(bouquets):
            for key, value in bouquet.items():
                assert response[i][key] == value

    @patch("services.crm_interface.coql_query_executor.execute_query")
    def test_fetch_first_products_bouquets_empty(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test fetch_first_product_bouquets, empty data."""
        get_mock.return_value = {"data": [], "info": {"more_records": False}}
        response = product_detail_operations.fetch_first_products_bouquets(
            faker.slug(), faker.slug()
        )
        assert not response
        assert isinstance(response, List)
