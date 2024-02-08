"""Module for 'mainpage' app crm entities handlers."""
from services.coql_handlers import COQLHandler

from .coql_queries import coql_queries as queries

additional_products_handler = COQLHandler(queries.get_additional_products_query)
