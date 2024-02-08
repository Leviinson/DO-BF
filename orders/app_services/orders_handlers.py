"""Orders handlers."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Union

import httpx
from dotenv import load_dotenv
from zcrmsdk.src.com.zoho.crm.api import Initializer
from zcrmsdk.src.com.zoho.crm.api.record import Record
from zcrmsdk.src.com.zoho.crm.api.util import APIHTTPConnector, Choice

from config.constants import Constants
from products.app_services.data_getters import crm_data as products_crm_data
from services.crm_interface import custom_record_operations
from services.data_getters import crm_data

load_dotenv()


class IndividualOrderHandlers:
    """Individual order handlers class."""

    @staticmethod
    async def create_individual_order(
        customer_id: Union[str, None],
        customer_name: str,
        customer_phone_number: str,
        min_budget: float,
        max_budget: float,
        photo=None,
    ):
        """
        To create an individual order record.

        Args:
            customer_id (Union[str, None]): Customer's ID if authenticated, else None.
            customer_name (str): Customer's name.
            customer_phone_number (str): Customer's phone number.
            min_budget (float): Minimum budget for the order.
            max_budget (float): Maximum budget for the order.
            photo: Optional photo data for the order.

        Returns:
            object: The created individual order record.

        Example:
            create_individual_order(
                customer_id='12345',
                customer_name='John Doe',
                customer_phone_number='555-555-5555',
                min_budget=100.0,
                max_budget=500.0,
                photo=None
            )
        """
        data = {}
        if customer_id:
            record: Record = Record()
            record.set_id(customer_id)
            data["customer_id"] = record
        data["status"] = Choice("В ожидании")
        data["customer_name"] = customer_name
        data["customer_phone_number"] = customer_phone_number
        data["budget_from"] = min_budget
        data["budget_to"] = max_budget
        return await custom_record_operations.create_records(
            "individual_orders",
            [
                data,
            ],
            photo,
        )


individual_order_handlers = IndividualOrderHandlers()


class QuickOrdersHandlers:
    """
    A class for handling quick orders.

    This class provides methods for creating quick orders in the ZohoCRM.
    """

    @staticmethod
    async def create_quick_order(
        product_id: int,
        customer_name: str,
        customer_phone_number: str,
        customer_id: Union[int, None] = None,
    ):
        """
        Create a quick order in the ZohoCRM.

        :param product_id: The ID of the product for the quick order.
        :param customer_name: The name of the customer placing the quick order.
        :param customer_phone_number: The phone number of the customer.
        :param customer_id: The ID of the customer (if available), or None.

        Returns:
        The created quick order record in the ZohoCRM or None if the creation fails.
        """
        data = {}
        if customer_id:
            record: Record = Record()
            record.set_id(customer_id)
            data["customer_id"] = record
        record: Record = Record()
        record.set_id(int(product_id))
        data["product_id"] = record
        data["status"] = Choice("В ожидании")
        data["customer_name"] = customer_name
        data["customer_phone_number"] = customer_phone_number
        return await custom_record_operations.create_records(
            "quick_orders",
            [
                data,
            ],
        )


quick_order_handlers = QuickOrdersHandlers()


class OrderHandlers:
    """Class containing static methods for handling orders."""

    def __init__(self):
        """Initialize image loader with an APIHTTPConnector."""
        self.connector = APIHTTPConnector()
        self.connector.url = Constants.COQL_REQUEST_URL

    async def get_not_existent_products(self, products_id_list: set[str]) -> list[str | None]:
        """
        Retrieve a list of non-existent products asynchronously.

        Args:
            products_id_list (List[str]): A list of product IDs to check.

        Returns:
            List[Union[str, None]]: A list of non-existent product IDs.

        Example:
            products = await self.get_not_existent_products(["id1", "id2"])
        """
        with ThreadPoolExecutor() as executor:
            executor.submit(Initializer.get_initializer().token.authenticate, self.connector)

        coroutines = []
        async with httpx.AsyncClient(
            headers=self.connector.headers,
            base_url="https://www.zohoapis.eu/crm/v5/products_base/",
        ) as client:
            for product_id in products_id_list:
                coroutines.append(self.__get_not_existent_product(client, product_id))
            result = await asyncio.gather(*coroutines)
        return {i for i in result if i is not None}

    @staticmethod
    async def __get_not_existent_product(
        client: httpx.AsyncClient, product_id: str
    ) -> str | None:
        """
        Check if a product exists asynchronously.

        Args:
            client (httpx.AsyncClient): An instance of httpx.AsyncClient.
            product_id (str): The ID of the product to check.

        Returns:
            Union[str, None]: The product ID if it does not exist, otherwise None.
        """
        response = await client.get(product_id)
        if response.status_code == 204:
            return product_id

    async def create_order(
        self,
        cart_products: list[str],
        order_number: str,
        region_slug: str,
        selected_currency: dict[str, Any],
        order_data: dict[str, datetime.date | Any],
    ) -> dict[str, Any]:
        """To create an order based on provided customer and delivery information.

        Args:
            *args: Variable-length argument list.
            **kwargs: Variable-length keyword argument list. Expected keyword arguments:
                - customer_phone_number (str): The customer's phone number.
                - name (str): The customer's name.
                - email (str): The customer's email address.
                - recipientName (str): The recipient's name.
                - recipient_phone_number (str): The recipient's phone number.
                - is_anonym (bool): Indicates whether the order should be anonymous.
                - is_surprise (bool): Indicates whether the order is a surprise.
                - ask_recipient_address (bool): Indicates if the recipient's address provided.
                - is_buyer_recipient (bool): Indicates if the buyer is also the recipient.
                - country (str): The delivery country.
                - city (str): The delivery city.
                - street (str): The delivery street.
                - house (str): The delivery building/house number.
                - flat (str): The delivery apartment/flat number.
                - date (date): The target delivery date.
                - postcard (str): The content of the postcard (optional).

        Returns:
            dict[str, Any]: This method returns base order data after creation.

        Example:
            OrderHandlers.create_order(
                customer_phone_number="123456789",
                name="John Doe",
                email="john@example.com",
                recipientName="Jane Doe",
                recipient_phone_number="987654321",
                is_anonym=False,
                is_surprise=True,
                ask_recipient_address=True,
                is_buyer_recipient=False,
                street="Example Street",
                building="42",
                flat="A1",
                date=datetime.date(2023, 1, 1),
                postcard="Happy Birthday!"
            )
        """
        data = {}
        data["order_number"] = order_number
        data["order_status"] = "В ожидании"
        data["customer_phone_number"] = order_data["customer_phone_number"]
        data["customer_name"] = order_data["customer_name"]
        data["Email"] = order_data["customer_email"]

        if order_data.get("recipient_name") and order_data.get("recipient_phone_number"):
            data["recipient_name"] = order_data["recipient_name"]
            data["recipient_phone_number"] = order_data["recipient_phone_number"]

        data["is_anonym"] = order_data["is_anonym"]
        data["is_surprise"] = order_data["is_surprise"]
        data["is_recipient"] = order_data["recipient_is_customer"]
        data["ask_recipient_address"] = order_data["ask_recipient_address"]
        data["target_delivery_date"] = order_data["date"].strftime("%Y-%m-%d")
        data["delivery_country"] = order_data["country"]
        data["delivery_city"] = order_data["city"]
        if not order_data["ask_recipient_address"]:
            if address := order_data["address"]:
                data["delivery_street"] = address["street"]
                data["delivery_building"] = address["building"]
            data["delivery_appartment"] = order_data["flat"]
        data["valentine"] = order_data["postcard"]
        region_products = await crm_data.get_region_products(
            region_slug, currency=selected_currency, cart_ids_set=None
        )
        created_order_json = await self.create_order_record(
            data, cart_products, region_products, selected_currency
        )
        return created_order_json

    async def create_order_record(
        self,
        order_data: dict[str, Any],
        cart_products: list[dict[str, Any]],
        region_products: list[dict[str, Any]],
        selected_currency: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create an order record asynchronously.

        Args:
            order_data (Dict[str, Any]): Information about the order.
            cart_products (Dict[str, Any]): Products in the shopping cart.

        Returns:
            Dict[str, Any]: Information about the created order.

        Example:
            order_data = {...}  # Your order data
            cart_products = {...}  # Your cart products
            result = await create_order_record(order_data, cart_products)
        """
        with ThreadPoolExecutor() as executor:
            executor.submit(Initializer.get_initializer().token.authenticate, self.connector)
        async with httpx.AsyncClient(headers=self.connector.headers) as client:
            json_data = {
                "data": [
                    order_data,
                ]
            }
            json_data["data"][0]["ordered_products"] = []
            grand_total = 0.0
            for product in cart_products:
                if region_product := next(
                    filter(lambda x: x["id"] == product["id"], region_products), None
                ):
                    if region_product["category_slug"] == "bouquets" and product.get("size"):
                        region_product.update(
                            await products_crm_data.get_product_bouquet_data(
                                region_product["id"],
                                currency=selected_currency,
                                discount=region_product["discount"],
                            )
                        )
                        for size_record in region_product["bouquet_sizes"]:
                            if size_record["value"] == product.get("size"):
                                bouquet_size_price = size_record[
                                    "price"
                                ]  # TODO: delete deprecated bouquet size
                                json_data["data"][0]["ordered_products"].append(
                                    {
                                        "product_id": product["id"],
                                        "amount": product["amount"],
                                        "size": product.get("size"),
                                        "price": bouquet_size_price,
                                    }
                                )
                                grand_total += bouquet_size_price
                                break
                    else:
                        price = (
                            region_product.get("new_price")
                            if region_product.get("discount")
                            else region_product["unit_price"]
                        )
                        json_data["data"][0]["ordered_products"].append(
                            {
                                "product_id": product["id"],
                                "amount": product["amount"],
                                "size": product.get("size"),
                                "price": price,
                            }
                        )
                        grand_total += price
            json_data["data"][0]["order_currency_id"] = selected_currency["id"]
            created_order_response = await client.post(
                url="https://www.zohoapis.eu/crm/v5/orders", json=json_data
            )
            created_order_json = created_order_response.json()
            created_order_json["data"][0]["grand_total"] = grand_total
            return created_order_json

    async def get_client_orders(self, orders_id_list: list[str]):
        """
        Retrieve order records for the specified order IDs.

        Args:
            orders_id_list (List[str]): A list of order IDs to retrieve records for.

        Returns:
            List[Optional[OrderRecord]]: A list of order records. If a record is not found for
            a particular order ID, the corresponding element in the list will be None.

        This asynchronous method retrieves order records for the provided list of order IDs.
        It utilizes an AsyncClient to make asynchronous HTTP requests to the Zoho CRM API
        for each order ID. The method returns a list of order records, and any order ID
        without a corresponding record will have a None value in the result list.
        """
        with ThreadPoolExecutor() as executor:
            executor.submit(Initializer.get_initializer().token.authenticate, self.connector)

        coroutines = []
        async with httpx.AsyncClient(
            headers=self.connector.headers,
            base_url="https://www.zohoapis.eu/crm/v5/orders/",
        ) as client:
            for order_id in orders_id_list:
                coroutines.append(self.__get_order_record(client, order_id))
            result = await asyncio.gather(*coroutines)
            return [i for i in result if i is not None]

    @staticmethod
    async def __get_order_record(client: httpx.AsyncClient, order_id: str) -> str | None:
        """
        Check if a product exists asynchronously.

        Args:
            client (httpx.AsyncClient): An instance of httpx.AsyncClient.
            product_id (str): The ID of the product to check.

        Returns:
            Union[str, None]: The product ID if it does not exist, otherwise None.
        """
        response = await client.get(order_id)
        if response.status_code == 200:
            return response.json()


order_handlers = OrderHandlers()
