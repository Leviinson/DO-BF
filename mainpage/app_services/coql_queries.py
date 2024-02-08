"""Module for creating coql queries for fetching Zoho CRM data."""


class COQLQueries:
    """Class for creating coql queries."""

    @staticmethod
    def get_additional_products_query(region_slug: str, subcategories_string: str) -> str:
        """Get coql query for fetching additional products."""
        return (
            f"select Name, unit_price, discount, subcategory_id.slug, region_id.slug "
            f"slug from products_base where "
            f"(is_recommended = true and is_active = true) "
            f"and (region_id.slug = '{region_slug}' and "
            f"subcategory_id.slug in {subcategories_string})"
            f" order by unit_price, discount desc"
        )


coql_queries = COQLQueries()
