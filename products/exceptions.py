"""Module containing custom exception classes for the 'Product' project."""


class ProductNotFoundError(Exception):
    """Custom exception class for indicating that a product was not found."""

    pass


class BouquetSizeNotFoundError(Exception):
    """Custom exception class for indicating that a bouquet size was not found."""

    pass


class DeprecatedBouquetSizeFoundError(Exception):
    """Custom exception class for indicating that a deprecated bouquet size was added into the cart."""
