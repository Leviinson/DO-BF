"""Module for 'API' project services handlers."""
from .coql_handlers import COQLHandler
from .coql_queries import coql_queries as queries
from .image_handlers import product_image_handler, subcategory_image_handler
from .utils import formatters

regions_handler = COQLHandler(queries.get_regions_query, (formatters.format_regions_list,))

regions_default_currencies_handler = COQLHandler(
    queries.get_regions_default_currencies,
    (formatters.format_regions_default_currencies,),
)

currency_handler = COQLHandler(
    queries.get_currency_query,
)

subcategories_handler = COQLHandler(
    queries.get_subcategories_list,
    (formatters.modify_subcategories, subcategory_image_handler.embed_subcategories_images),
)

categories_handler = COQLHandler(
    queries.get_categories_list,
)

region_products_handler = COQLHandler(
    queries.get_region_products_query,
    (formatters.format_product_list, product_image_handler.embed_products_image),
)
