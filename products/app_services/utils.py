"""Formatters for 'product' app."""

from typing import Any, Dict, List


class Formatters:
    """Class with methods for formatting dicts."""

    @staticmethod
    def modify_single_product_data(products: list[dict], **kwargs: Any) -> list:
        """Modify single product data for templates."""
        for product in products:
            product["country_name"] = product.pop("region_id.country_id.Name")
            product["region_name"] = product.pop("region_id.Name")
            product["subcategory_name"] = product.pop("subcategory_id.Name")
            product["category_name"] = product.pop("subcategory_id.category_id.Name")
        return products

    def modify_bouquet_data(self, bouquets_data: list[dict[str, str | dict]], **kwargs):
        """
        Modify bouquets data for templates.

        :param input_data: list[dict] Data dicts list for modifying.
        """
        result = {}
        for data in bouquets_data:
            if not result:
                result["bouquet_flowers"] = data.pop("bouquet_id.flowers")
                result["bouquet_flowers_amount"] = data.pop("amount_of_flowers")
                result["bouquet_colors"] = data.pop("bouquet_id.colors")
                result["bouquet_sizes"] = [
                    {"price": data.get("price"), "value": data.get("value")},
                ]
            else:
                result["bouquet_sizes"].append(
                    {"price": data.get("price"), "value": data.get("value")}
                )
        return result

    @staticmethod
    def modify_first_nine_similar_bouquets_data(data: List[Dict], **kwargs) -> List[Dict]:
        """
        Modify dicts keys for Django templates.

        :param data: list[dict] List of dicts with bouquets products data.
        """
        region_products = kwargs["region_products"]
        for elem in data:
            elem["id"] = elem.pop("product_id.id")
            product_base = next(
                (product for product in region_products if product["id"] == elem["id"]), None
            )
            elem["subcategory_slug"] = product_base["subcategory_slug"]
            elem["Name"] = elem.pop("product_id.Name")
            elem["unit_price"] = elem.pop("product_id.unit_price")
            elem["discount"] = elem.pop("product_id.discount")
            elem["discount_start_date"] = elem.pop("product_id.discount_start_date")
            elem["discount_end_date"] = elem.pop("product_id.discount_end_date")
            elem["slug"] = elem.pop("product_id.slug")
            elem["is_recommended"] = elem.pop("product_id.is_recommended")
            elem["is_bouquet"] = elem.pop("product_id.is_bouquet")
        return data

    @staticmethod
    def filter_by_colors_and_flowers(
        products: list[dict[str, str]],
        colors: list[str] = None,
        flowers: list[str] = None,
        **kwargs,
    ) -> List[Dict]:
        """
        Filter bouquets by similar flowers and colors.

        Returns results in the descending order of similar flowers and colors
        plus adds bouquets, that are not similar if there is no another choice.
        """
        if colors and flowers:
            bouquets_colors_and_flowers_intersection = list(
                filter(
                    lambda bouquet: set(bouquet["colors"]).intersection(colors)
                    or set(bouquet["flowers"]).intersection(flowers),
                    products,
                )
            )
            mismatched_bouquets = [
                product
                for product in products
                if product not in bouquets_colors_and_flowers_intersection
            ]
            return bouquets_colors_and_flowers_intersection + mismatched_bouquets
        return []  # TODO: to handle absence of records in 'bouquets_sizes' module

    @staticmethod
    def limit_products_bouquets_to_nine(products: List[Dict], **kwargs) -> List[Dict]:
        """Limit products list to nine items."""
        return products[:9]


formatters = Formatters()
