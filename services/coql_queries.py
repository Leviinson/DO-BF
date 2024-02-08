"""Module for creating coql queries for fetching Zoho CRM data."""


class COQLQueries:
    """Class for creating coql queries."""

    @staticmethod
    def get_regions_query() -> str:
        """Create query for fetching region list."""
        return "select code, \
                       slug, \
                       Name, \
                       country_id.currency_id.Name, \
                       country_id.code, \
                       country_id.Name, \
                       local_phone_number_1, \
                       local_phone_number_2, \
                       telegram_link, \
                       viber_link, \
                       whatsapp_link, \
                       facebook_link, \
                       instagram_link, \
                       Email \
                       from regions where code is not null"

    @staticmethod
    def get_regions_default_currencies() -> str:
        """Create query for fetching region default currency."""
        return "select slug, \
                       country_id.currency_id.Name \
                from regions where code is not null"

    @staticmethod
    def get_currency_query() -> str:
        """Create query for fetching currency list."""
        return "select Name, \
                       symbol, \
                       static_exchange_rate \
                from currencies where Name is not null"

    @staticmethod
    def get_subcategories_list() -> str:
        """Create query for fetching subcategories info."""
        return (
            "select category_id.Name, category_id.slug, category_id.id, Name, slug from"
            " subcategories where Name is not null"
        )

    @staticmethod
    def get_categories_list() -> str:
        """Create query for fetching categories info."""
        return "select Name, slug from categories where Name is not null"

    @staticmethod
    def get_region_products_query(region_slug: str) -> str:
        """Create query for fetching region products."""
        return (
            f"select Name, sku, unit_price, discount, discount_start_date, region_id.slug, "
            f"discount_end_date, slug, is_recommended, is_bouquet, "
            f"subcategory_id.Name, subcategory_id.slug"
            f" from products_base where region_id.slug"
            f" = {region_slug} and is_active = true"
        )


coql_queries = COQLQueries()
