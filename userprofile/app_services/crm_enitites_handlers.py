"""Module for 'userprofile' app crm entities handlers."""
from services.coql_handlers import COQLHandler
from services.image_handlers import product_image_handler

from .coql_queries import coql_queries as queries
from .crm_utils import crm_formatters

customer_addresses_handler = COQLHandler(queries.get_customer_addresses_query)

customer_address_handler = COQLHandler(queries.get_customer_address_query)

customer_default_address_handler = COQLHandler(queries.get_customer_default_address_query)

customer_contacts_handler = COQLHandler(queries.get_customer_contacts_query)

customer_contact_handler = COQLHandler(queries.get_customer_contact_query)

customer_viewed_products_handler = COQLHandler(
    queries.get_customer_viewed_products_query,
    (crm_formatters.modify_products_dicts_list, product_image_handler.embed_products_image),
)
