class GrantTokenDoesNotExist(Exception):
    """Exception for grant token absence."""

    pass


class SDKTokenExpired(Exception):
    """Exception for grant token experation date."""

    pass
