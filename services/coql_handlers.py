"""Module for 'API' projects coql hadlers."""
import inspect
from types import MethodType
from typing import Any, Dict, List, Tuple, Union

from services.crm_interface import coql_query_executor


class COQLHandler:
    """Class for coql handlers functionality."""

    def __init__(
        self,
        query: MethodType,
        formatters: Tuple = tuple(),
        default: Any = None,
    ) -> None:
        """
        Initialize handler.

        :param query: MethodType Method for returning query for fetching data.
        :param formatters: Tuple Tuple of methods for received result formatting.
            Formatters will be used in the order they are listed in tuple. First
            will be used first, and so on. Formatters receive one positional -
            products_list, and many key-word arguments, that must be checkend in
            formatter body for existence.
        :param default: Any Default return for fethc_instances method in case of
            empty fetched list. Will be set to empty list in case of None value.
        """
        self.query = query
        self.formatters = formatters
        self.default = default if default else []

    async def fetch_instances(
        self, *coql_args: dict, lim: int = 200, **formatters_kwargs: dict
    ) -> Union[List, Dict]:
        """
        Fetch many instances from Zoho CRM.

        :param args: Optional positional arguments, used in creating coql query,
         for example: product_id, region_slug;
        :param kwargs: Optional key-word arguments, lim - int, offset - int, for
         pointing in fetch_data() to instantiate request offset and limit.

        In case of absence lim key-word argument data will be fetched all in
        accordance with 'where' query clause, pointing lim to some value lower
        then 200 will lead only for fetching that max amount of data.
        """
        query: str = self.query(*coql_args)
        result: List = await coql_query_executor.fetch_data(query, lim=lim)
        if result:
            for formatter in self.formatters:
                if inspect.iscoroutinefunction(formatter):
                    result = await formatter(result, **formatters_kwargs)
                else:
                    result = formatter(result, **formatters_kwargs)
            return result
        return self.default

    async def fetch_instance(self, *args: Any, **kwargs: Any) -> Dict:
        """
        Fetch single instance from Zoho CRM.

        Logic is the same as in 'fetch_instances', additinally add checking
        for the list with element and returning first list element (dict).
        """
        result: List = await self.fetch_instances(*args, **kwargs)
        if result:
            return result[0]
        return {}
