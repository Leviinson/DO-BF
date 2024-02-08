"""Module, that contains client interaction operations."""
import re
from typing import Dict, List, Optional, Union

from django.http import HttpRequest

from config.constants import Constants

from .data_getters import crm_data
from .utils import ip_geo_locator


class ClientInteractionHandler:
    """Handles client interactions."""

    def get_client_region_by_language_header(
        self, language_header: Union[str, None], regions: List[Dict[str, str]]
    ) -> Optional[str]:
        """
        Find the region based on the language header.

        It looks in the LANGUAGE_IDENTIFIERS_DICT and returns the corresponding region
        if found, otherwise returns None.

        Args:
            request (HttpRequest): The Django HttpRequest instance.

        Returns:
            Optional[str]: The region corresponding to the language header, if found.
        Otherwise, returns None.
        """
        if language_header:
            language_list: list = re.findall("[a-z]{2}", language_header)
            for elem in language_list:
                if elem in Constants.LANGUAGE_IDENTIFIERS_DICT:
                    return next(
                        (
                            region
                            for region in regions
                            if region["country_code"].lower()
                            == Constants.LANGUAGE_IDENTIFIERS_DICT[elem].lower()
                        ),
                        None,
                    )

    async def get_client_region(
        self, request: HttpRequest, regions: list[dict[str, str]]
    ) -> dict[str, str]:  # TODO take into account country and regions name changing
        """
        Get the region name of the client.

        It retrieves the region using the request IP, headers, Constants.DEFAULT_REGION
        in case of any problem with the Zoho CRM API connection, absence of the city in
        the regions list, or absence of the user's country in the countries list.

        Args:
            request (HttpRequest): The Django HttpRequest instance.

        Returns:
            str: The region name.
        """
        location_data: Dict = await crm_data.get_location(ip_geo_locator.get_client_ip(request))

        countries_codes = (region["country_code"] for region in regions)
        for region in regions:
            if (
                (region_code := location_data.get("city"))
                and region_code == region.get("code")
                or (country := location_data.get("country"))
                and country in countries_codes
            ):
                return region

        if region := self.get_client_region_by_language_header(
            request.headers.get("Accept-Language"), regions
        ):
            return region


client_handler = ClientInteractionHandler()
