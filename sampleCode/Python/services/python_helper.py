from datetime import timedelta

def pretty_timedelta(elapsed: timedelta) -> str:
    """
    Get a more readable representation of a timedelta value
    """
    if elapsed.days >= 0:
        return str(elapsed)
    return f"-({-elapsed!s})"

