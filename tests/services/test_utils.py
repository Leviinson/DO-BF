"""Module for testing services.utils."""
from copy import deepcopy
from typing import Dict, List, Set, Tuple

import pytest
from asgiref.sync import async_to_sync
from django.http import HttpRequest
from faker import Faker

from services.utils import (
    convert_bouquet_sizes_prices,
    convert_price,
    convert_product_price,
    convert_products_prices,
    formatters,
    ip_geo_locator,
    mark_products_in_cart,
    utilities,
)


class TestGetClientIp:
    """Class for testing ip_geo_locator.get_client_ip."""

    def test_get_client_ip_with_forwarded_for(
        self,
        get_fake_meta_headers: HttpRequest,
    ) -> None:
        """Test utils.utilities.get_client_ip. With HTTP_X_FORWARDED_FOR."""
        request: HttpRequest = get_fake_meta_headers
        expected_ip: str = request.META.get("REMOTE_ADDR")
        request.META["HTTP_X_REAL_IP"] = None
        request.META["REMOTE_ADDR"] = None
        result: str = ip_geo_locator.get_client_ip(request)
        assert expected_ip == result

    def test_get_client_ip_with_real_ip(
        self,
        get_fake_meta_headers: HttpRequest,
    ) -> None:
        """Test utils.ip_geo_locator.get_client_ip. Without HTTP_X_FORWARDED_FOR."""
        request: HttpRequest = get_fake_meta_headers
        expected_ip: str = request.META.get("REMOTE_ADDR")
        request.META["HTTP_X_FORWARDED_FOR"] = None
        request.META["REMOTE_ADDR"] = None
        result: str = ip_geo_locator.get_client_ip(request)
        assert expected_ip == result

    def test_get_client_ip_with_remote_addr(
        self,
        get_fake_meta_headers: HttpRequest,
    ) -> None:
        """Test utils.ip_geo_locator.get_client_ip. Without HTTP_X_FORWARDED_FOR."""
        request: HttpRequest = get_fake_meta_headers
        expected_ip: str = request.META.get("REMOTE_ADDR")
        request.META["HTTP_X_FORWARDED_FOR"] = None
        request.META["HTTP_X_REAL_IP"] = None
        result: str = ip_geo_locator.get_client_ip(request)
        assert expected_ip == result


class TestFetchLocation:
    """Class for testing ip_geo_locator.fetch_location."""

    def test_fetch_location_krakow(self) -> None:
        """Test fetch_location using Krakow ip."""
        result = async_to_sync(ip_geo_locator.fetch_location)("31.182.221.88")
        assert result.get("ip") == "31.182.221.88"
        assert result.get("city") == "Krakow"
        assert result.get("region") == "Lesser Poland"
        assert result.get("country") == "Poland"

    def test_fetch_location_berlin(self) -> None:
        """Test fecth_location using Berlin ip."""
        result = async_to_sync(ip_geo_locator.fetch_location)("85.214.132.117")
        assert result.get("ip") == "85.214.132.117"
        assert result.get("city") == "Berlin"
        assert result.get("region") == "Land Berlin"
        assert result.get("country") == "Germany"

    def test_fetch_location_local(self) -> None:
        """Test fetch_location using local ip."""
        result = async_to_sync(ip_geo_locator.fetch_location)("0.0.0.0")
        assert result.get("ip") == "0.0.0.0"
        assert not result.get("city")
        assert not result.get("region")
        assert not result.get("country")


class TestIncludeProductCartAmount:
    """Class for testing formatters.include_product_cart_amount method."""

    def test_include_product_cart_amount(self, faker: Faker) -> None:
        """Test include_product_cart_amount method."""
        product: Dict = {}
        amount: str = str(faker.random_int())
        result = formatters.include_product_cart_amount(product, amount)
        assert result["cart_amount"] == amount


class TestFormatCartProducts:
    """Class for testing formatters.format_cart_products method."""

    async def test_format_cart_products(
        self,
        faker: Faker,
        get_fake_region_products: List[Dict],
    ) -> None:
        """Test format_cart_products method."""
        products: List[Dict] = get_fake_region_products
        cart_products = faker.random_elements(elements=products, unique=True, length=5)
        cart = {product.get("id"): faker.random_int(min=1) for product in cart_products}
        result = await formatters.format_cart_products(cart, products)
        for product in cart_products:
            flag = False
            for expected_product in result:
                if product.get("id") == expected_product.get("id"):
                    flag = True
                    for key, value in product.items():
                        assert expected_product[key] == value
                    assert expected_product["cart_amount"] == cart.get(expected_product["id"])
                    break
            if not flag:
                assert False


class TestModifySubCategories:
    """Class for testing formatters.modify_subcategories."""

    def test_modify_subcategories(
        self,
        get_response_subcategories_list: Tuple[List, List],
    ) -> None:
        """Test modify_categories method."""
        input_list, expected_result = get_response_subcategories_list
        result: List = formatters.modify_subcategories(input_list)
        for i, item in enumerate(result):
            for key, value in result[i].items():
                assert item[key] == value


class TestFormatCategoriesAndRelatedSubcategories:
    """Class for testing formatters.format_categories_and_related_subcategories."""

    def test_format_categories_and_related_subcategories(
        self,
        get_response_format_categories_and_related_subcategories: Tuple[List, List],
        get_response_subcategories_list: Tuple[List, List],
    ) -> None:
        """Test formatters.format_categories_and_related_subcategories."""
        categories, expected_output = get_response_format_categories_and_related_subcategories
        input_list, subcategories = get_response_subcategories_list
        result = formatters.format_categories_and_related_subcategories(
            categories, subcategories
        )
        for i, item in enumerate(expected_output):
            for key, value in result[i].items():
                if key == "subcategories":
                    for j, elem in enumerate(value):
                        for k, v in item["subcategories"][j].items():
                            assert elem[k] == v
                else:
                    assert item[key] == value


@pytest.mark.django_db
class TestCreateRegionDict:
    """Class for testing formatters.create_region_dict method."""

    @pytest.mark.django_db
    def test_create_region_dict(self, get_regions_data: Tuple[List[Dict], List[Dict]]) -> None:
        """Test formatters.create_region_dict method."""
        regions, expected_output = get_regions_data
        result = async_to_sync(formatters.format_regions_list)(regions)
        for i, region in enumerate(expected_output):
            for key, value in result[i].items():
                assert region[key] == value


class TestFormatProductList:
    """Class for testing formatters.format_product_list."""

    def test_format_product_list(
        self,
        faker: Faker,
        get_fake_region_products: List[Dict],
    ) -> None:
        """Test formatters.format_product_list."""
        products: List[Dict] = get_fake_region_products
        expected_products: List = []
        subcategories: List = []
        for product in products:
            expected_product = product.copy()
            region_slug = expected_product["region_slug"] = expected_product.pop(
                "region_id.slug"
            )
            expected_product["subcategory_name"] = expected_product.pop("subcategory_id.Name")
            subcat_slug = expected_product["subcategory_slug"] = expected_product.pop(
                "subcategory_id.slug"
            )
            category_slug = faker.pystr(min_chars=3)
            expected_product["category_slug"] = category_slug
            expected_product["url"] = f"/product/{region_slug}/{subcat_slug}/{product['slug']}"
            expected_products.append(expected_product)
            subcategories.append(
                {
                    "slug": product.get("subcategory_id.slug"),
                    "category_slug": category_slug,
                }
            )
            for i in range(3):
                subcategories.append({"slug": faker.pystr(min_chars=4)})
        result = async_to_sync(formatters.format_product_list)(
            products, subcategories=subcategories
        )
        for i, product in enumerate(expected_products):
            for key, value in result[i].items():
                if key == "url":
                    assert value.endswith(product[key])
                else:
                    assert product[key] == value


@pytest.mark.django_db
class TestFormatRegionsDefaultCurrencies:
    """Class for testing formatters.format_regions_default_currencies."""

    @pytest.mark.django_db
    def test_format_regions_default_currencies(
        self, get_regions_data: Tuple[List[Dict], List[Dict]]
    ) -> None:
        """Test formatters.format_regions_default_currencies."""
        regions, data = get_regions_data
        expected_output: Dict = {
            currency.get("slug"): currency.get("default_currency") for currency in data
        }
        result = formatters.format_regions_default_currencies(data)
        for key, value in expected_output.items():
            assert result[key] == value


class TestFormatUserData:
    """Class for testing formatters.format_user_data."""

    def test_format_user_data(self, faker: Faker) -> None:
        """Test formatters.format_user_data."""
        email: str = faker.email()
        username: str = faker.user_name()
        phone_number: str = faker.phone_number()
        result = formatters.format_user_data(
            {"email": email, "username": username, "phone_number": phone_number}
        )
        assert result["Name"] == username
        assert result["Email"] == email
        assert result["phone_number"] == phone_number


class TestGetSelectedCurrency:
    """Class for testing utilites.get_selected_currency."""

    def test_get_selected_currency(
        self, faker: Faker, get_fake_currency_list: List[Dict[str, int]]
    ) -> None:
        """Test utilites.get_selected_currency."""
        currency_list: List[Dict[str, int]] = get_fake_currency_list
        expected_result: Dict = faker.random_element(elements=currency_list)
        result = utilities.get_selected_currency(currency_list, expected_result.get("Name"))
        for key, value in expected_result.items():
            assert result[key] == value

    def test_get_selected_currency_absent(
        self, faker: Faker, get_fake_currency_list: List[Dict[str, int]]
    ) -> None:
        """Test utilites.get_selected_currency, qparam not in the list case."""
        currency_list: List[Dict[str, int]] = get_fake_currency_list
        result = utilities.get_selected_currency(currency_list, faker.pystr(min_chars=1))
        assert result is None


class TestGetMinMaxBudget:
    """Class for testing utilites.get_min_max_budget."""

    def test_get_min_max_budget(self, faker: Faker) -> None:
        """Test utilities.get_min_max_budget."""
        min_value: float = faker.pyfloat(min_value=0, max_value=100)
        max_value: float = faker.pyfloat(min_value=0, max_value=100)
        result = utilities.get_min_max_budget(str(min_value), str(max_value))
        assert result[0] == min_value
        assert result[1] == max_value

    def test_get_min_max_budget_empty_min(self, faker: Faker) -> None:
        """Test utilities.get_min_max_budget."""
        max_value: float = faker.pyfloat(min_value=0, max_value=100)
        result = utilities.get_min_max_budget(None, str(max_value))
        assert result[0] is None
        assert result[1] == max_value

    def test_get_min_max_budget_empty_max(self, faker: Faker) -> None:
        """Test utilities.get_min_max_budget."""
        min_value: float = faker.pyfloat(min_value=0, max_value=100)
        result = utilities.get_min_max_budget(str(min_value), None)
        assert result[0] == min_value
        assert result[1] is None

    def test_get_min_max_budget_empty_both(self, faker: Faker) -> None:
        """Test utilities.get_min_max_budget."""
        result = utilities.get_min_max_budget(None, None)
        assert result[0] is None
        assert result[1] is None

    def test_get_min_max_budget_not_number(self, faker: Faker) -> None:
        """Test utilities.get_min_max_budget."""
        min_value: str = faker.email()
        max_value: float = faker.pyfloat(min_value=0, max_value=100)
        result = utilities.get_min_max_budget(min_value, str(max_value))
        assert result[0] is None
        assert result[1] is None


class TestConvertProductsPrices:
    """Class for testing convert_products_prices decorator."""

    def test_convert_products_prices(
        self, faker: Faker, get_fake_region_products: List[Dict]
    ) -> None:
        """Test convert_products_prices decorator."""
        products: List[Dict] = get_fake_region_products
        currency_symbol, currency_name = faker.currency()
        currency: Dict = {
            "id": faker.random_int(min=999999999999, max=1000000000000),
            "Name": currency_name,
            "symbol": currency_symbol,
            "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
        }
        expected_products = deepcopy(products)

        @convert_products_prices
        def test_func(**kwargs):
            return products

        result = async_to_sync(test_func)(currency=currency)
        for i, product in enumerate(expected_products):
            for key, value in result[i].items():
                if key == "unit_price":
                    assert value == round(
                        float(product[key]) / currency["static_exchange_rate"], 2
                    )
                elif key == "discount":
                    assert product[key] == value
                    if value:
                        assert result[i]["new_price"] == round(
                            (result[i]["unit_price"] * (100 - product[key])) / 100, 2
                        )
                elif key == "currency_symbol":
                    assert value == currency["symbol"]
                elif key == "new_price":
                    pass
                else:
                    assert product[key] == value

    def test_convert_products_prices_async(
        self, faker: Faker, get_fake_region_products: List[Dict]
    ) -> None:
        """Test convert_products_prices decorator."""
        products: List[Dict] = get_fake_region_products
        currency_symbol, currency_name = faker.currency()
        currency: Dict = {
            "id": faker.random_int(min=999999999999, max=1000000000000),
            "Name": currency_name,
            "symbol": currency_symbol,
            "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
        }
        expected_products = deepcopy(products)

        @convert_products_prices
        async def test_func(**kwargs):
            return products

        result = async_to_sync(test_func)(currency=currency)
        for i, product in enumerate(expected_products):
            for key, value in result[i].items():
                if key == "unit_price":
                    assert value == round(
                        float(product[key]) / currency["static_exchange_rate"], 2
                    )
                elif key == "discount":
                    assert product[key] == value
                    if value:
                        assert result[i]["new_price"] == round(
                            (result[i]["unit_price"] * (100 - product[key])) / 100, 2
                        )
                elif key == "currency_symbol":
                    assert value == currency["symbol"]
                elif key == "new_price":
                    pass
                else:
                    assert product[key] == value

    def test_convert_products_prices_empty_discount(
        self, faker: Faker, get_fake_region_products: List[Dict]
    ) -> None:
        """Test convert_products_prices decorator."""
        products: List[Dict] = get_fake_region_products
        for product in products:
            product["discount"] = None
        currency_symbol, currency_name = faker.currency()
        currency: Dict = {
            "id": faker.random_int(min=999999999999, max=1000000000000),
            "Name": currency_name,
            "symbol": currency_symbol,
            "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
        }
        expected_products = deepcopy(products)

        @convert_products_prices
        def test_func(**kwargs):
            return products

        result = async_to_sync(test_func)(currency=currency)
        for i, product in enumerate(expected_products):
            for key, value in result[i].items():
                if key == "unit_price":
                    assert value == round(
                        float(product[key]) / currency["static_exchange_rate"], 2
                    )
                elif key == "currency_symbol":
                    assert value == currency["symbol"]
                else:
                    assert product[key] == value


class TestConvertProductPrice:
    """Class for testing convert_product_price decorator."""

    def test_convert_product_price(
        self, faker: Faker, get_fake_region_products: List[Dict]
    ) -> None:
        """Test convert_product_price decorator."""
        product: Dict = get_fake_region_products[0]
        currency_symbol, currency_name = faker.currency()
        currency: Dict = {
            "id": faker.random_int(min=999999999999, max=1000000000000),
            "Name": currency_name,
            "symbol": currency_symbol,
            "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
        }
        expected_product = deepcopy(product)

        @convert_product_price
        def test_func(**kwargs):
            return product

        result = async_to_sync(test_func)(currency=currency)
        for key, value in result.items():
            if key == "unit_price":
                assert value == round(
                    float(expected_product[key]) / currency["static_exchange_rate"], 2
                )
            elif key == "discount":
                assert expected_product[key] == value
                if value:
                    assert result["new_price"] == round(
                        (result["unit_price"] * (100 - expected_product[key])) / 100, 2
                    )
            elif key == "currency_symbol":
                assert value == currency["symbol"]
            elif key == "new_price":
                pass
            else:
                assert expected_product[key] == value

    def test_convert_product_price_async(
        self, faker: Faker, get_fake_region_products: List[Dict]
    ) -> None:
        """Test convert_products_prices decorator."""
        product: Dict = get_fake_region_products[0]
        currency_symbol, currency_name = faker.currency()
        currency: Dict = {
            "id": faker.random_int(min=999999999999, max=1000000000000),
            "Name": currency_name,
            "symbol": currency_symbol,
            "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
        }
        expected_product = deepcopy(product)

        @convert_product_price
        async def test_func(**kwargs):
            return product

        result = async_to_sync(test_func)(currency=currency)
        for key, value in result.items():
            if key == "unit_price":
                assert value == round(
                    float(expected_product[key]) / currency["static_exchange_rate"], 2
                )
            elif key == "discount":
                assert expected_product[key] == value
                if value:
                    assert result["new_price"] == round(
                        (result["unit_price"] * (100 - expected_product[key])) / 100, 2
                    )
            elif key == "currency_symbol":
                assert value == currency["symbol"]
            elif key == "new_price":
                pass
            else:
                assert expected_product[key] == value

    def test_convert_product_price_empty_discount(
        self, faker: Faker, get_fake_region_products: List[Dict]
    ) -> None:
        """Test convert_products_prices decorator."""
        product: Dict = get_fake_region_products[0]
        product["discount"] = None
        currency_symbol, currency_name = faker.currency()
        currency: Dict = {
            "id": faker.random_int(min=999999999999, max=1000000000000),
            "Name": currency_name,
            "symbol": currency_symbol,
            "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
        }
        expected_product = deepcopy(product)

        @convert_product_price
        def test_func(**kwargs):
            return product

        result = async_to_sync(test_func)(currency=currency)
        for key, value in result.items():
            if key == "unit_price":
                assert value == round(
                    float(expected_product[key]) / currency["static_exchange_rate"], 2
                )
            elif key == "currency_symbol":
                assert value == currency["symbol"]
            else:
                assert expected_product[key] == value


class TestConvertPrice:
    """Class for testing convert_price functionality."""

    def test_convert_price(
        self,
        get_fake_region_products: List[Dict],
        faker: Faker,
    ) -> None:
        """Test convert_price functionality."""
        product: Dict = get_fake_region_products[0]
        currency_symbol, currency_name = faker.currency()
        currency: Dict = {
            "id": faker.random_int(min=999999999999, max=1000000000000),
            "Name": currency_name,
            "symbol": currency_symbol,
            "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
        }
        expected_product = deepcopy(product)
        convert_price(expected_product, currency, expected_product["discount"])
        assert expected_product["unit_price"] == round(
            float(product["unit_price"]) / currency["static_exchange_rate"], 2
        )
        assert expected_product["new_price"] == round(
            expected_product["unit_price"] * (100 - product["discount"]) / 100, 2
        )
        assert expected_product["currency_symbol"] == currency["symbol"]

    def test_convert_price_empty_discount(
        self,
        get_fake_region_products: List[Dict],
        faker: Faker,
    ) -> None:
        """Test convert_price functionality."""
        product: Dict = get_fake_region_products[0]
        product["discount"] = None
        currency_symbol, currency_name = faker.currency()
        currency: Dict = {
            "id": faker.random_int(min=999999999999, max=1000000000000),
            "Name": currency_name,
            "symbol": currency_symbol,
            "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
        }
        expected_product = deepcopy(product)
        convert_price(expected_product, currency, expected_product["discount"])
        assert expected_product["unit_price"] == round(
            float(product["unit_price"]) / currency["static_exchange_rate"], 2
        )
        assert expected_product.get("new_price") is None
        assert expected_product["currency_symbol"] == currency["symbol"]

    def test_convert_price_another_key(
        self,
        get_fake_region_products: List[Dict],
        faker: Faker,
    ) -> None:
        """Test convert_price functionality."""
        product: Dict = get_fake_region_products[0]
        price_key: str = faker.pystr(min_chars=5)
        product[price_key] = product["unit_price"]
        currency_symbol, currency_name = faker.currency()
        currency: Dict = {
            "id": faker.random_int(min=999999999999, max=1000000000000),
            "Name": currency_name,
            "symbol": currency_symbol,
            "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
        }
        expected_product = deepcopy(product)
        convert_price(
            expected_product, currency, expected_product["discount"], price_key=price_key
        )
        assert expected_product[price_key] == round(
            float(product[price_key]) / currency["static_exchange_rate"], 2
        )
        assert expected_product["new_price"] == round(
            expected_product[price_key] * (100 - product["discount"]) / 100, 2
        )
        assert expected_product["currency_symbol"] == currency["symbol"]


class TestConvertBouqetSizesPrices:
    """Class for testing convert_bouquet_sizes_prices decorator."""

    def test_convert_bouquet_sizes_prices(
        self, faker: Faker, get_fake_bouquet_sizes: Tuple[List[Dict], Dict]
    ) -> None:
        """Test convert_bouquet_sizes_prices decorator."""
        input_list, input_dict = get_fake_bouquet_sizes
        bouquet_data = deepcopy(input_dict)
        currency_symbol, currency_name = faker.currency()
        currency: Dict = {
            "id": faker.random_int(min=999999999999, max=1000000000000),
            "Name": currency_name,
            "symbol": currency_symbol,
            "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
        }
        discount = faker.pyfloat(min_value=0, max_value=100)

        @convert_bouquet_sizes_prices
        async def get_data(**kwargs):
            return bouquet_data

        result = async_to_sync(get_data)(currency=currency, discount=discount)
        assert result["bouquet_flowers"] == input_dict["bouquet_flowers"]
        assert result["bouquet_flowers_amount"] == input_dict["bouquet_flowers_amount"]
        assert result["bouquet_colors"] == input_dict["bouquet_colors"]
        for i, bouquet_size in enumerate(result["bouquet_sizes"]):
            for key, value in bouquet_size.items():
                if key == "price":
                    assert value == round(
                        input_dict["bouquet_sizes"][i]["price"]
                        / currency["static_exchange_rate"],
                        2,
                    )
                elif key == "new_price":
                    assert value == round(
                        result["bouquet_sizes"][i]["price"] * (100 - discount) / 100, 2
                    )
                elif key == "currency_symbol":
                    assert value == currency["symbol"]
                else:
                    assert input_dict["bouquet_sizes"][i][key] == value

    def test_convert_bouquet_sizes_prices_empty_discount(
        self, faker: Faker, get_fake_bouquet_sizes: Tuple[List[Dict], Dict]
    ) -> None:
        """Test convert_bouquet_sizes_prices decorator."""
        input_list, input_dict = get_fake_bouquet_sizes
        bouquet_data = deepcopy(input_dict)
        currency_symbol, currency_name = faker.currency()
        currency: Dict = {
            "id": faker.random_int(min=999999999999, max=1000000000000),
            "Name": currency_name,
            "symbol": currency_symbol,
            "static_exchange_rate": faker.random_int(min=10, max=1000) / 100,
        }
        discount = None

        @convert_bouquet_sizes_prices
        async def get_data(**kwargs):
            return bouquet_data

        result = async_to_sync(get_data)(currency=currency, discount=discount)
        assert result["bouquet_flowers"] == input_dict["bouquet_flowers"]
        assert result["bouquet_flowers_amount"] == input_dict["bouquet_flowers_amount"]
        assert result["bouquet_colors"] == input_dict["bouquet_colors"]
        for i, bouquet_size in enumerate(result["bouquet_sizes"]):
            for key, value in bouquet_size.items():
                if key == "price":
                    assert value == round(
                        input_dict["bouquet_sizes"][i]["price"]
                        / currency["static_exchange_rate"],
                        2,
                    )
                elif key == "currency_symbol":
                    assert value == currency["symbol"]
                else:
                    assert input_dict["bouquet_sizes"][i][key] == value


class TestMarkProductsInCart:
    """Class for testing mark_products_in_cart decorator."""

    def test_mark_products_in_cart(
        self,
        faker: Faker,
        get_fake_region_products: List[Dict],
    ) -> None:
        """Test mark_products_in_cart decorator."""
        products = get_fake_region_products
        id_set: Set = set()
        for product in products:
            if faker.pybool():
                id_set.add(product["id"])

        @mark_products_in_cart
        async def get_products(**kwargs):
            return products

        result = async_to_sync(get_products)(cart_ids_set=id_set)
        for product in result:
            if product["id"] in id_set:
                assert product["is_in_cart"]
            else:
                assert not product["is_in_cart"]

    def test_mark_products_in_cart_without_is_list(
        self,
        faker: Faker,
        get_fake_region_products: List[Dict],
    ) -> None:
        """Test mark_products_in_cart decorator."""
        products = get_fake_region_products

        @mark_products_in_cart
        async def get_products(**kwargs):
            return products

        result = async_to_sync(get_products)()
        for product in result:
            assert not product["is_in_cart"]
