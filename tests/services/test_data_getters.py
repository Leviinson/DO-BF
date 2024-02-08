"""Module for testing services.data_getters."""
from typing import Dict, List, Tuple
from unittest.mock import AsyncMock, patch

from asgiref.sync import async_to_sync
from django.core.cache import cache
from faker import Faker

from services.data_getters import crm_data
from services.utils import formatters
from tests.conftest import compare_dicts, compare_lists_dicts


class TestGetLocation:
    """Class for testing CRMData get_location method."""

    @patch("services.utils.ip_geo_locator.fetch_location", new_callable=AsyncMock)
    def test_get_location(
        self,
        mock_location_data: AsyncMock,
        faker: Faker,
    ) -> None:
        """Test get_location method."""
        ip: str = faker.ipv4_public()
        location: Dict = {
            "ip": ip,
            "city": faker.city(),
            "region": faker.city(),
            "country": faker.country(),
        }
        new_location: Dict = {
            "ip": faker.ipv4_public(),
            "city": faker.city(),
            "region": faker.city(),
            "country": faker.country(),
        }
        mock_location_data.return_value = location
        result = async_to_sync(crm_data.get_location)(ip)
        compare_dicts(location, result)
        mock_location_data.return_value = new_location
        result = async_to_sync(crm_data.get_location)(ip)
        compare_dicts(location, result)
        cache.clear()
        result = async_to_sync(crm_data.get_location)(ip)
        compare_dicts(new_location, result)


class TestGetRegionsList:
    """Class for testing CRMData get_regions_list method."""

    @patch(
        "services.crm_entities_handlers.regions_handler.fetch_instances", new_callable=AsyncMock
    )
    def test_get_regions_list(
        self,
        mock_regions_handler: AsyncMock,
        faker: Faker,
        get_faker_regions: Tuple[List[Dict[str, int]], Dict[str, str]],
    ) -> None:
        """Test get_regions_list method."""
        regions, new_regions = get_faker_regions
        mock_regions_handler.return_value = regions
        result = async_to_sync(crm_data.get_regions_list)()
        compare_lists_dicts(regions, result)
        mock_regions_handler.return_value = [new_regions]
        result = async_to_sync(crm_data.get_regions_list)()
        compare_lists_dicts(regions, result)
        cache.clear()
        result = async_to_sync(crm_data.get_regions_list)()
        compare_lists_dicts([new_regions], result)


class TestGetRegionsDefaultCurrencies:
    """Class for testing CRMData get_regions_default_currencies method."""

    @patch(
        "services.crm_entities_handlers.regions_default_currencies_handler.fetch_instances",
        new_callable=AsyncMock,
    )
    def test_get_regions_default_currencies(
        self,
        mock_currencies: AsyncMock,
        get_fake_currency_list: List[Dict[str, int]],
    ) -> None:
        """Test get_regions_default_currencies."""
        currency: List[Dict[str, int]] = get_fake_currency_list
        mock_currencies.return_value = currency[0]
        result = async_to_sync(crm_data.get_regions_default_currencies)()
        compare_dicts(currency[0], result)
        mock_currencies.return_value = currency[1]
        result = async_to_sync(crm_data.get_regions_default_currencies)()
        compare_dicts(currency[0], result)
        cache.clear()
        result = async_to_sync(crm_data.get_regions_default_currencies)()
        compare_dicts(currency[1], result)


class TestGetRegionProducts:
    """Class for testing CRMData get_region_products method."""

    @patch(
        "services.crm_entities_handlers.region_products_handler.fetch_instances",
        new_callable=AsyncMock,
    )
    @patch("services.data_getters.crm_data.get_subcategories_list", new_callable=AsyncMock)
    def test_get_region_products(
        self,
        mock_subcategories: AsyncMock,
        mock_regions: AsyncMock,
        faker: Faker,
        get_fake_region_products: List[Dict],
    ) -> None:
        """Test get_region_products."""
        regions: List[Dict] = async_to_sync(formatters.format_product_list)(
            get_fake_region_products, subcategories=[]
        )

        mock_subcategories.return_value = []
        mock_regions.return_value = regions
        #   TODO not finished
