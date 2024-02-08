"""Module for testing mainpage app_services coql_queries."""
from faker import Faker

from mainpage.app_services.coql_queries import coql_queries


class TestGetAdditionalProductsQuery:
    """Class for testing get_additional_products_query method."""

    def test_get_additional_products_query(self, faker: Faker) -> None:
        """Test get_additional_products_query."""
        region_slug: str = faker.slug()
        subcategories_string: str = faker.pystr(min_chars=1, max_chars=20)
        result: str = coql_queries.get_additional_products_query(
            region_slug, subcategories_string
        )
        assert result == (
            f"select Name, unit_price, discount, subcategory_id.slug, region_id.slug "
            f"slug from products_base where "
            f"(is_recommended = true and is_active = true) "
            f"and (region_id.slug = '{region_slug}' and "
            f"subcategory_id.slug in {subcategories_string})"
            f" order by unit_price, discount desc"
        )
