"""Module for testing products.app_services.utils functionality."""
from typing import Dict, List, Tuple

from faker import Faker

from products.app_services.utils import formatters


class TestModifySingleProductData:
    """Class for testing formatters.modify_single_product_data."""

    def test_modify_single_product_data(
        self,
        faker: Faker,
        create_single_product_fake_data: Tuple[Dict, Dict],
    ) -> None:
        """Test modify_single_product_data."""
        input_dict, expected_dict = create_single_product_fake_data
        response = formatters.modify_single_product_data(input_dict)
        for key, value in response.items():
            assert expected_dict[key] == value


class TestConvertBouquetData:
    """Class for testing formatters.convert_bouquet_data."""

    def test_convert_bouquet_data(
        self,
        faker: Faker,
        create_single_product_fake_bouquet_data: Tuple[List[Dict], Dict],
    ) -> None:
        """Test convert_bouquet_data."""
        input_list, expected_dict = create_single_product_fake_bouquet_data
        response = formatters.convert_bouquet_data(input_list)
        assert isinstance(response, Dict)
        for i, item in enumerate(response.get("bouquets_sizes")):
            assert item["price"] == expected_dict["bouquets_sizes"][i]["price"]
            assert item["value"] == expected_dict["bouquets_sizes"][i]["value"]


class TestModifyBouquetsData:
    """Class for testing formatters.modify_bouquets_data."""

    def test_modify_bouquets_data(
        self,
        create_single_product_fake_bouquet_data: Tuple[List[Dict], Dict],
    ) -> None:
        """Test modify_bouquets_data."""
        input_list, expected_dict = create_single_product_fake_bouquet_data
        response = formatters.modify_bouquets_data(input_list)
        for key, value in response.items():
            if key == "bouquets_sizes":
                for i, item in enumerate(response[key]):
                    assert item.get("price") == expected_dict.get("bouquets_sizes")[i].get(
                        "price"
                    )
                    assert item.get("value") == expected_dict.get("bouquets_sizes")[i].get(
                        "value"
                    )
            else:
                assert expected_dict[key] == value


class TestModifyFirstNineSubcategoryBouquetsData:
    """Test formatters.modify_first_nine_subcategory_bouquets_data."""

    def test_modify_first_nine_subcategory_bouquets_data(
        self,
        create_fake_products_bouquets: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """Test modify_first_nine_subcategory_bouquets_data."""
        input_list, expected_list = create_fake_products_bouquets
        response = formatters.modify_first_nine_subcategory_bouquets_data(input_list)
        for i, item in enumerate(input_list):
            for key, value in item.items():
                assert response[i][key] == value
