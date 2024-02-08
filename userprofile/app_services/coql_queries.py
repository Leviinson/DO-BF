"""Module for creating coql queries fetching Zoho CRM data for 'userprofile' app."""


class COQLQueries:
    """Class for creating coql queries."""

    @staticmethod
    def get_customer_addresses_query(customer_id: int) -> str:
        """Create query for fetching customer addresses."""
        return (
            f"select Name, country, city, street, building, appartment, is_default"
            f" from customer_addresses where customer_id.id = {customer_id} "
            f"order by is_default desc"
        )

    @staticmethod
    def get_customer_address_query(address_id: int) -> str:
        """Create query for fetching customer address."""
        return (
            f"select Name, country, city, street, building, appartment, is_default"
            f" from customer_addresses where id = {address_id}"
        )

    @staticmethod
    def get_customer_default_address_query(customer_id: int) -> str:
        """Create query for fetching customer default address."""
        return (
            f"select Name from customer_addresses where customer_id.id = {customer_id}"
            f" and is_default = true"
        )

    @staticmethod
    def get_customer_contacts_query(customer_id: int) -> str:
        """Create query for fetching customer contacts."""
        return (
            f"select Name, phone_number from customer_contacts where "
            f"customer_id.id = {customer_id}"
        )

    @staticmethod
    def get_customer_contact_query(contact_id: int) -> str:
        """Create query for fetching customer contact."""
        return f"select Name, phone_number from customer_contacts where " f"id = {contact_id}"

    @staticmethod
    def get_customer_viewed_products_query(ids_string) -> str:
        """Create query for fetching customer viewed products."""
        return (
            f"select Name, unit_price, discount, slug, "
            f"region_id.slug, subcategory_id.slug, subcategory_id.category_id "
            f"from products_base where id in {ids_string}"
        )


coql_queries = COQLQueries()
