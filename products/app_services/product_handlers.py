"""Functionality for getting data for 'products' app."""

from typing import Dict, List, Optional, Union

from products.app_services.data_getters import crm_data
from services.crm_interface import custom_record_operations


class ProductDetailHandlers:
    """Class for getting product data for ProductView."""

    @staticmethod
    async def get_product_details_for_product_view(
        region_slug: str, subcategory_slug: str, product_slug: str, currency: dict[str, str]
    ) -> Dict:
        """
        Prepare product detail data for ProductView.

        :param region_slug: str Region slug.
        :param subcategory_slug: str Subcategory slug.
        :param product_slug: str Product slug.
        """
        product_dict: Dict = await crm_data.get_product_details(
            region_slug, subcategory_slug, product_slug, currency=currency
        )
        if product_dict.get("is_bouquet"):
            product_id: int = product_dict.get("id")
            product_dict.update(
                await crm_data.get_product_bouquet_data(
                    product_id, currency=currency, discount=product_dict["discount"]
                )
            )
        return product_dict

    @staticmethod
    async def get_first_nine_similar_products(
        region_slug: str,
        subcategory_slug: str,
        product_id: str,
        colors: list | None,
        flowers: list | None,
        is_bouquet: bool | None,
        currency: dict[str, str | float],
        region_products: list[dict[str, str]],
    ) -> List:
        """
        Get first nine subcategory products for ProductView.

        :param region_slug: str Products region slug.
        :param subcategory_slug: str Products subcategory slug.
        :param product_id: str Product id.
        :param colors: Optional[list] Colors list.
        :param flowers: Optional[list] Flowers list.
        :param is_bouquet: Optional[bool] Whether the product is_bouquet.
        """
        if is_bouquet:
            return await crm_data.get_first_nine_similar_bouquets(
                region_slug,
                product_id,
                colors=colors,
                flowers=flowers,
                currency=currency,
                region_products=region_products,
            )
        return [
            product
            for product in region_products
            if product["subcategory_slug"] == subcategory_slug and product["id"] != product_id
        ]

    @staticmethod
    def update_ordered_product(ordered_product_id: str, amount: int) -> Optional[int]:
        """
        Update ordered_products record in Zoho CRM.

        :param ordered_product_id: int Product id in Zoho CRM.
        :param amount: int New product amount in Zoho CRM.
        """
        return custom_record_operations.update_record(
            "ordered_products",
            int(ordered_product_id),
            {"amount": amount},
        )

    @staticmethod
    def delete_ordered_product(
        ordered_product_id: str,
    ) -> bool:
        """
        Delete ordered_products record in Zoho CRM.

        :param ordered_product_id: int Ordered_products record id in Zoho CRM.
        """
        return custom_record_operations.delete_record(
            "ordered_products",
            int(ordered_product_id),
        )

    def search_region_products(
        self,
        region_products: List[Dict[str, str]],
        name: Union[str, None] = None,
        subcategory_slug: Union[str, None] = None,
        min_budget: Union[float, None] = None,
        max_budget: Union[float, None] = None,
    ) -> List[Dict]:
        """
        Fetch products data from Zoho CRM using search query.

        Single-Parameter Filtering

        :param region_products: List of product dictionaries for the region.
        :param selected_currency: Dictionary containing selected currency data.
        :param name: Name of the product to search for.
        :param subcategory_slug: Subcategory slug to filter products.
        :param min_budget: Minimum budget for filtering products.
        :param max_budget: Maximum budget for filtering products.
        :return: List of filtered product dictionaries.
        """
        searched_products = []
        if name and not subcategory_slug and min_budget is None and max_budget is None:
            searched_products = self._filter_by_name(region_products, name)
        else:
            searched_products = self._filter_by_subcategory_or_budget(
                region_products,
                subcategory_slug,
                min_budget,
                max_budget,
            )
        return searched_products[:4] if len(searched_products) >= 4 else searched_products

    def _filter_by_name(self, region_products: List[Dict[str, str]], name: str) -> List[Dict]:
        """
        Filter products by name.

        :param region_products: List of product dictionaries for the region.
        :param selected_currency: Dictionary containing selected currency data.
        :param name: Name of the product to search for.
        :return: List of filtered product dictionaries.
        """
        filtered_products = []

        for product in region_products:
            if name.lower() in product["Name"].lower():
                product["image_url"] = product.pop("image").url
                filtered_products.append(product)

        return filtered_products

    def _filter_by_subcategory_or_budget(
        self,
        region_products: List[Dict[str, str]],
        subcategory_slug: str,
        min_budget: float,
        max_budget: float,
    ) -> List[Dict]:
        """
        Filter products by subcategory and budget range.

        :param region_products: List of product dictionaries for the region.
        :param selected_currency: Dictionary containing selected currency data.
        :param subcategory_slug: Subcategory slug to filter products.
        :param min_budget: Minimum budget for filtering products.
        :param max_budget: Maximum budget for filtering products.
        :return: List of filtered product dictionaries.
        """
        filtered_products = []
        for product in region_products:
            if subcategory_slug and not product["subcategory_slug"].lower() == subcategory_slug:
                continue
            elif not self._is_product_price_fits_budget(product, min_budget, max_budget):
                continue
            product["image_url"] = product.pop("image").url
            filtered_products.append(product)
        return filtered_products

    @staticmethod
    def _is_product_price_fits_budget(product: dict[str, str], min_budget, max_budget: float):
        """
        Check if a product's price falls within the specified budget range.

        Args:
            product (dict): A dictionary containing information about the product.
            min_budget (float): The minimum budget threshold.
            max_budget (float): The maximum budget threshold.

        Returns:
            bool: True if the product's price is within the budget range, False otherwise.
        """
        if product.get("new_price"):
            price = product["new_price"]
        else:
            price = product["unit_price"]

        if not ((min_budget <= price <= max_budget)):
            return False
        return True


product_detail_handlers = ProductDetailHandlers()
