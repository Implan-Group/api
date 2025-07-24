from datetime import timedelta
from uuid import UUID

"""
This prelude contains some useful methods for accessing the API and debugging
"""


def uuid_empty() -> UUID:
    """
    Returns an all-zero UUID
    """
    return UUID(int=0)


def print_timedelta(elapsed: timedelta) -> str:
    """
    Get a more readable representation of a timedelta value
    """
    if elapsed.days >= 0:
        return str(elapsed)
    return f"-({-elapsed!s})"