from concurrent.futures import ThreadPoolExecutor
from pprint import pprint

import httpx
from django.core.cache import cache
from zcrmsdk.src.com.zoho.crm.api import Initializer
from zcrmsdk.src.com.zoho.crm.api.util import APIHTTPConnector


class CRMData:
    def __init__(self):
        """Initialize image loader with an APIHTTPConnector."""
        self.connector = APIHTTPConnector()

    async def get_bouquets_module_fields(self):
        if fields := cache.get("bouquets_module_fields"):
            return fields
        with ThreadPoolExecutor() as executor:
            executor.submit(Initializer.get_initializer().token.authenticate, self.connector)
        async with httpx.AsyncClient(headers=self.connector.headers) as client:
            response = await client.get(
                url="https://www.zohoapis.eu/crm/v5/settings/fields?module=bouquets"
            )
        if response.status_code == 200:
            pprint(response.json())
        pprint(response.json())


crm_data = CRMData()
