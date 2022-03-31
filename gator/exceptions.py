class GatorError(Exception):
    """Base class for all handled errors in our system."""


class InvalidSpecificationError(GatorError):
    """There was an error with retrieving specification data."""
