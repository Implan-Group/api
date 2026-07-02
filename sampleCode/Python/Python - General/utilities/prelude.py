import json
from datetime import timedelta
from enum import Enum
from pprint import pprint
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


def pretty_print(obj):
    """Pretty print anything - handles objects, lists of objects, dicts, etc."""

    def serialize(o):
        # Handle Enums
        if isinstance(o, Enum):
            # For str-based Enums, use the name; otherwise use value
            if isinstance(o.value, str):
                return o.name
            return o.value
        # handle objects with a __dict__ attribute
        if hasattr(o, '__dict__'):
            return o.__dict__
        # handle lists + tuples
        elif isinstance(o, (list, tuple)):
            return [serialize(item) for item in o]
        # handle dicts
        elif isinstance(o, dict):
            return {k: serialize(v) for k, v in o.items()}
        return o

    # use json.dumps with the serialized payload and use str as a fallback
    try:
        serialized = serialize(obj)
        print(json.dumps(serialized, indent=2, default=str))
    except (TypeError, ValueError) as e:
        # If JSON fails for any reason, fall back to pprint
        print("JSON serialization failed, using pprint:")
        pprint(obj)