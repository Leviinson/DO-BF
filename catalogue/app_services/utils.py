"""Represents general utils."""
from enum import Enum

from services.data_getters import crm_data
from services.utils import mark_products_in_cart


class BreadCrumbs:
    """To create dict of catalogue breadcrumbs."""

    @staticmethod
    async def get_category_crumb(category_slug: str) -> dict[str, str]:
        """To create dict of category breadcrumb."""
        categories = await crm_data.get_categories_list()
        cat_slug, cat_title = next(
            ((cat["slug"], cat["Name"]) for cat in categories if cat["slug"] == category_slug),
            None,
        )
        return {"slug": cat_slug, "title": cat_title}

    @staticmethod
    async def get_subcategory_crumb(subcategory_slug: str) -> dict[str, str]:
        """To create dict of subcategory breadcrumb."""
        subcategories = await crm_data.get_subcategories_list()
        cat_slug, cat_title = next(
            (
                (subcat["slug"], subcat["Name"])
                for subcat in subcategories
                if subcat["slug"] == subcategory_slug
            ),
            None,
        )
        return {"slug": cat_slug, "title": cat_title}


bread_crumbs = BreadCrumbs()


class Filter:
    """To filter products in the catalogue."""

    @staticmethod
    @mark_products_in_cart
    async def filter_products(
        region: str,
        category_slug: str,
        subcategory_slug: str | None,
        currency: dict[str, str],
        sorting: str,
        cart_ids_set: list[str],
    ) -> list[dict[str, str]]:
        """
        Get filtered products based on the specified category and subcategory slugs.

        Args:
            region (str): The region identifier.
            category_slug (str): The slug of the category to filter products.
            subcategory_slug (str or None): The slug of the subcategory to
            filter products, or None if no subcategory filtering is needed.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing filtered products.
        """

        class Sorting(str, Enum):
            RECOMMENDED = "rec"
            DISCOUNT = "disc"
            CHEAPEST = "low"
            EXPENSIVE = "high"

        if subcategory_slug:
            filtered_products = [
                product
                for product in await crm_data.get_region_products(
                    region["slug"], currency=currency
                )
                if product["subcategory_slug"] == subcategory_slug
            ]
        else:
            filtered_products = [
                product
                for product in await crm_data.get_region_products(
                    region["slug"], currency=currency
                )
                if product["category_slug"] == category_slug
            ]
        match sorting:
            case None:
                return filtered_products
            case Sorting.RECOMMENDED:
                return sorted(
                    filtered_products, key=lambda x: x["is_recommended"], reverse=True
                )
            case Sorting.DISCOUNT:
                return sorted(filtered_products, key=lambda x: x["discount"], reverse=True)
            case Sorting.CHEAPEST:
                return sorted(
                    filtered_products,
                    key=lambda x: x["new_price"] if x["discount"] else x["unit_price"],
                )
            case Sorting.EXPENSIVE:
                return sorted(
                    filtered_products,
                    key=lambda x: x["new_price"] if x["discount"] else x["unit_price"],
                    reverse=True,
                )
            case _:
                return filtered_products


filters = Filter()
