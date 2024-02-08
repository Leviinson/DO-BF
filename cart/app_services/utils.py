from copy import copy
from typing import Any

from products.app_services.data_getters import crm_data
from products.exceptions import DeprecatedBouquetSizeFoundError


class Formatters:
    @staticmethod
    def include_product_cart_amount(product: dict, amount: str) -> dict:
        """
        Include the cart amount for a product.

        Args:
            product (dict): The product dictionary to include the cart amount in.
            amount (str): The cart amount to set for the product.

        Returns:
            product (dict)
        """
        product["cart_amount"] = amount
        return product

    @staticmethod
    async def include_bouquets_sizes(
        region_product: dict[str, Any],
        cart_product: dict[str, int | str],
        currency: dict[str, str | float],
        cart: dict[str, Any],
    ) -> dict[str, Any]:
        if region_product["category_slug"] == "bouquets":
            region_product.update(
                await crm_data.get_product_bouquet_data(
                    region_product["id"], currency=currency, discount=region_product["discount"]
                )
            )
            bouquet_size_from_cart = cart_product["size"]
            if not bouquet_size_from_cart:
                region_product["selected_size"] = "Стандартный"
                return region_product
            else:
                for size_record in region_product["bouquet_sizes"]:
                    if size_record["value"] == bouquet_size_from_cart:
                        region_product["selected_size"] = bouquet_size_from_cart
                        region_product["unit_price"] = size_record["price"]
                        if new_price := size_record.get("new_price"):
                            region_product["new_price"] = new_price
                        break
                else:
                    raise DeprecatedBouquetSizeFoundError()
        return region_product

    @classmethod
    async def format_cart_products(
        cls,
        cart: dict[str, Any],
        region_products: list[dict[str, Any]],
        currency: dict[str, str | float],
    ) -> list[dict[str, str]]:
        """
        Format cart products based on the given cart and region products.

        Removes bouquets because of the deprecated sizes.

        Args:
            cart_products (dict): A dictionary containing product IDs and their
                respective cart amounts.
            region_products (list): A list of product dictionaries for a specific region.

        Returns:
            list[dict]: A list of formatted product dictionaries with cart amounts included.
        """
        result = []
        filtered_region_products = tuple(
            filter(
                lambda x: x["id"] in (cart_product["id"] for cart_product in cart["products"]),
                region_products,
            )
        )
        for product in filtered_region_products:
            for cart_product in cart["products"]:
                if cart_product["id"] == product["id"]:
                    product_copy = copy(product)
                    cls.include_product_cart_amount(product_copy, cart_product["amount"])
                    try:
                        await cls.include_bouquets_sizes(
                            product_copy, cart_product, currency, cart
                        )
                    except DeprecatedBouquetSizeFoundError():
                        continue
                    result.append(product_copy)
        return result


formatters = Formatters()
