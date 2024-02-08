"""Module for 'product' app crm entities handlers."""
from services.coql_handlers import COQLHandler
from services.image_handlers import product_image_handler

from .coql_queries import coql_queries as queries
from .utils import formatters

product_details_handler = COQLHandler(
    queries.get_product_details_query,
    (
        formatters.modify_single_product_data,
        product_image_handler.embed_products_image,
    ),
)

product_bouquet_handler = COQLHandler(
    queries.get_product_bouquet_data_query,
    (formatters.modify_bouquet_data,),
)

first_nine_similar_bouquets_handler = COQLHandler(
    queries.get_similar_bouquets,
    (
        formatters.filter_by_colors_and_flowers,
        # formatters.limit_products_bouquets_to_nine, # TODO: check necessaribility
        formatters.modify_first_nine_similar_bouquets_data,
        product_image_handler.embed_products_image,
    ),
)

ordered_product_handler = COQLHandler(queries.get_ordered_product_query)
