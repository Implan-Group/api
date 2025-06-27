from datetime import timedelta
from uuid import UUID


def pretty_timedelta(elapsed: timedelta) -> str:
    """
    Get a more readable representation of a timedelta value
    """
    if elapsed.days >= 0:
        return str(elapsed)
    return f"-({-elapsed!s})"

def uuid_empty() -> UUID:
    return UUID(int=0)
