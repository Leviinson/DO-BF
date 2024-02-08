"""Module for creating coql queries for fetching Zoho CRM data for 'product' api."""


class COQLQueries:
    """Class for creating 'product' api coql queries."""

    @staticmethod
    def get_product_details_query(
        region_slug: str,
        subcategory_slug: str,
        product_slug: str,
    ) -> str:
        """Get query for fetching product details."""
        return (
            f"select sku, region_id.country_id.Name, region_id.Name, "
            f"subcategory_id.Name, subcategory_id.slug, subcategory_id.category_id.Name,"
            f" Name, unit_price, discount, discount_start_date, "
            f"discount_end_date, desc, specs, is_bouquet from "
            f"products_base where (region_id.slug = {region_slug}"
            f" and is_active = true) and ((subcategory_id.slug = "
            f"'{subcategory_slug}') and slug = '{product_slug}')"
        )

    @staticmethod
    def get_product_bouquet_data_query(
        product_id: int,
    ) -> str:
        """Get query for fetching product bouquet data query."""
        return (
            f"select value, price, bouquet_id.flowers, "
            f"amount_of_flowers, bouquet_id.colors "
            f"from bouquets_sizes where bouquet_id.product_id.id "
            f"= {product_id}"
        )

    @staticmethod
    def get_similar_bouquets(region_slug: str, product_id: str) -> str:
        """Get query for fetching region products bouquets."""
        return (
            f"select product_id.Name, product_id.unit_price, "
            f"product_id.discount, product_id.discount_start_date, "
            f"product_id.discount_end_date, product_id.slug, "
            f"product_id.is_recommended, product_id.is_bouquet, "
            f"product_id.id, flowers, colors from bouquets where "
            f"(product_id.is_active = true and product_id != "
            f"{product_id}) and product_id.region_id.slug = "
            f"'{region_slug}' order by product_id.is_recommended, "
            f"product_id.discount desc"
        )

    @staticmethod
    def get_ordered_product_query(customer_id: int, product_id: int) -> str:
        """Get query for fetching ordered product id."""
        return (
            f"select id from ordered_products where product_id.id "
            f"= {product_id} and (order_id is null and customer_id.id "
            f"= {customer_id})"
        )


coql_queries = COQLQueries()
