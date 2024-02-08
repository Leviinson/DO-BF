"""Module for testing services.client_handlers."""
from typing import Dict, List, Tuple
from unittest.mock import MagicMock, patch

from django.http import HttpRequest
from django.utils.text import slugify
from faker import Faker

from config.constants import Constants
from services.caching import caching
from services.client_handlers import client_handler
from tests.services.conftest import ModHttpRequest


class TestGetRegionByCountryName:
    """Class for testing client_handler.get_region_by_country_name."""

    @patch("services.caching.caching.get_country_dict")
    def test_get_region_by_country_name_region_in_dict(
        self,
        get_mock: MagicMock,
        get_faker_countries: Tuple[List[Dict], Dict],
        faker: Faker,
    ) -> None:
        """Test client_handler.get_region_by_country_name. Region in country dict."""
        region: str = faker.city()
        input_country_list, output_country_dict = get_faker_countries
        number = faker.random_int(max=len(input_country_list) - 1)
        country: str = input_country_list[number].get("code")
        output_country_dict[country] = region
        get_mock.return_value = output_country_dict
        result_region: str = client_handler.get_client_region_by_country_name(country)
        assert region == result_region

    @patch("services.crm_entities_interaction.zoho_data.fetch_region_by_country_name")
    @patch("services.caching.caching.get_country_dict")
    def test_get_region_by_country_name_region_not_in_dict(
        self,
        get_mock_1: MagicMock,
        get_mock_2: MagicMock,
        get_faker_countries: Tuple[List[Dict], Dict],
        faker: Faker,
    ) -> None:
        """Test client_handler.get_client_region_by_country_name. Region not in countries."""
        region: str = faker.city()
        input_country_list, output_country_dict = get_faker_countries
        number = faker.random_int(max=len(input_country_list) - 1)
        country: str = input_country_list[number].get("code")
        get_mock_1.return_value = output_country_dict
        get_mock_2.return_value = [{"code": region}]
        expected_region: str = client_handler.get_client_region_by_country_name(country)
        assert region == expected_region
        country_dict: Dict = caching.get_country_dict()
        assert country_dict[country] == expected_region

    @patch("services.crm_entities_interaction.zoho_data.fetch_region_by_country_name")
    @patch("services.caching.caching.get_country_dict")
    def test_get_region_by_country_name(
        self,
        get_mock_1: MagicMock,
        get_mock_2: MagicMock,
        get_faker_countries: Tuple[List[Dict], Dict],
        faker: Faker,
    ) -> None:
        """Test client_handler.get_client_region_by_country_name. Region not in countries."""
        input_country_list, output_country_dict = get_faker_countries
        number = faker.random_int(max=len(input_country_list) - 1)
        country: str = input_country_list[number].get("code")
        get_mock_1.return_value = output_country_dict
        get_mock_2.return_value = None
        expected_region: str = client_handler.get_client_region_by_country_name(country)
        assert Constants.DEFAULT_REGION == expected_region


class TestGetClientRegionByLanguageHeader:
    """Class for testing client_handler.get_client_region_by_language_header."""

    @patch("services.client_handlers.client_handler.get_client_region_by_country_name")
    def test_get_client_region_by_language_header_ua(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test get_client_region_by_language_header."""
        request = ModHttpRequest(
            {"Accept-Language": "uk-UA,uk;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6,en;q=0.5"}
        )
        get_mock.side_effect = lambda x: x
        response = client_handler.get_client_region_by_language_header(request)
        assert response == "Ukraine"

    @patch("services.client_handlers.client_handler.get_client_region_by_country_name")
    def test_get_client_region_by_language_header_de(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test get_client_region_by_language_header."""
        request = ModHttpRequest(
            {"Accept-Language": "de-DE,de;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6,en;q=0.5"}
        )
        get_mock.side_effect = lambda x: x
        response = client_handler.get_client_region_by_language_header(request)
        assert response == "Germany"


class TestGetClientRegion:
    """Class for testing client_handler.get_client_region."""

    @patch("services.caching.caching.get_country_dict")
    @patch("services.caching.caching.get_region_dict")
    @patch("services.caching.caching.get_location")
    def test_get_client_region_location_with_region(
        self,
        get_mock_location: MagicMock,
        get_mock_region: MagicMock,
        get_mock_countries: MagicMock,
        get_fake_location_data: Dict,
        get_faker_regions: Tuple[List[Dict[str, int]], Dict[str, str]],
        get_faker_countries: Tuple[List[Dict[str, int]], Dict],
        faker: Faker,
    ) -> None:
        """Test get_client_region."""
        request = HttpRequest()
        location: Dict = get_fake_location_data
        regions: Dict = get_faker_regions[1]
        countries: Dict = dict()
        regions[location.get("city")] = slugify(location.get("city"))
        get_mock_location.return_value = location
        get_mock_region.return_value = regions
        get_mock_countries.return_value = countries
        response = client_handler.get_client_region(request)
        assert response == regions.get(location.get("city"))

    @patch("services.caching.caching.get_country_dict")
    @patch("services.caching.caching.get_region_dict")
    @patch("services.caching.caching.get_location")
    def test_get_client_region_location_with_country(
        self,
        get_mock_location: MagicMock,
        get_mock_region: MagicMock,
        get_mock_countries: MagicMock,
        get_fake_location_data: Dict,
        get_faker_regions: Tuple[List[Dict[str, int]], Dict[str, str]],
        get_faker_countries: Tuple[List[Dict[str, int]], Dict],
        faker: Faker,
    ) -> None:
        """Test get_client_region."""
        request = HttpRequest()
        location: Dict = get_fake_location_data
        regions: Dict = get_faker_regions[1]
        countries: Dict = get_faker_countries[1]
        location["city"] = None
        expected_region = faker.city()
        countries[location.get("country")] = expected_region
        get_mock_location.return_value = location
        get_mock_region.return_value = regions
        get_mock_countries.return_value = countries
        response = client_handler.get_client_region(request)
        assert response == regions.get(expected_region)

    @patch("services.caching.caching.get_country_dict")
    @patch("services.caching.caching.get_region_dict")
    @patch("services.caching.caching.get_location")
    def test_get_client_region_location_with_country_region_not_in(
        self,
        get_mock_location: MagicMock,
        get_mock_region: MagicMock,
        get_mock_countries: MagicMock,
        get_fake_location_data: Dict,
        get_faker_regions: Tuple[List[Dict[str, int]], Dict[str, str]],
        get_faker_countries: Tuple[List[Dict[str, int]], Dict],
        faker: Faker,
    ) -> None:
        """Test get_client_region."""
        request = HttpRequest()
        location: Dict = get_fake_location_data
        regions: Dict = get_faker_regions[1]
        countries: Dict = get_faker_countries[1]
        location["city"] = faker.pystr(min_chars=2, max_chars=10)
        expected_region = faker.city()
        countries[location.get("country")] = expected_region
        get_mock_location.return_value = location
        get_mock_region.return_value = regions
        get_mock_countries.return_value = countries
        response = client_handler.get_client_region(request)
        assert response == regions.get(expected_region)

    @patch("services.client_handlers.client_handler.get_client_region_by_country_name")
    @patch("services.caching.caching.get_country_dict")
    @patch("services.caching.caching.get_region_dict")
    @patch("services.caching.caching.get_location")
    def test_get_client_region_location_with_country_without_region(
        self,
        get_mock_location: MagicMock,
        get_mock_region: MagicMock,
        get_mock_countries: MagicMock,
        get_mock_client: MagicMock,
        get_fake_location_data: Dict,
        get_faker_regions: Tuple[List[Dict[str, int]], Dict[str, str]],
        get_faker_countries: Tuple[List[Dict[str, int]], Dict],
        faker: Faker,
    ) -> None:
        """Test get_client_region."""
        request = HttpRequest()
        location: Dict = get_fake_location_data
        regions: Dict = get_faker_regions[1]
        countries: Dict = get_faker_countries[1]
        location["city"] = None
        expected_region = faker.city()
        countries[location.get("country")] = None
        get_mock_location.return_value = location
        get_mock_region.return_value = regions
        get_mock_countries.return_value = countries
        get_mock_client.return_value = expected_region
        response = client_handler.get_client_region(request)
        assert response == regions.get(expected_region)

    @patch("services.client_handlers.client_handler.get_client_region_by_language_header")
    @patch("services.caching.caching.get_country_dict")
    @patch("services.caching.caching.get_region_dict")
    @patch("services.caching.caching.get_location")
    def test_get_client_region_location_with_region_header(
        self,
        get_mock_location: MagicMock,
        get_mock_region: MagicMock,
        get_mock_countries: MagicMock,
        get_mock_header: MagicMock,
        get_fake_location_data: Dict,
        faker: Faker,
    ) -> None:
        """Test get_client_region."""
        request = HttpRequest()
        location: Dict = get_fake_location_data
        location["city"] = None
        location["country"] = None
        expected_region = faker.city()
        get_mock_location.return_value = location
        get_mock_region.return_value = {expected_region: slugify(expected_region)}
        get_mock_countries.return_value = dict()
        get_mock_header.return_value = expected_region
        response = client_handler.get_client_region(request)
        assert response == slugify(expected_region)

    @patch("services.client_handlers.client_handler.get_client_region_by_language_header")
    @patch("services.caching.caching.get_country_dict")
    @patch("services.caching.caching.get_region_dict")
    @patch("services.caching.caching.get_location")
    def test_get_client_region_location_with_region_header_empty(
        self,
        get_mock_location: MagicMock,
        get_mock_region: MagicMock,
        get_mock_countries: MagicMock,
        get_mock_header: MagicMock,
        get_fake_location_data: Dict,
        faker: Faker,
    ) -> None:
        """Test get_client_region."""
        request = HttpRequest()
        location: Dict = get_fake_location_data
        location["city"] = None
        location["country"] = None
        get_mock_location.return_value = location
        get_mock_region.return_value = {
            Constants.DEFAULT_REGION: slugify(Constants.DEFAULT_REGION)
        }
        get_mock_countries.return_value = dict()
        get_mock_header.return_value = None
        response = client_handler.get_client_region(request)
        assert response == slugify(Constants.DEFAULT_REGION)
