import json
from datetime import timedelta
from typing import Any
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

def inspect(thing):
    # if thing is a list, tuple or set
    # recursively call inspect on everything inside the list/tuple/set
    if type(thing) in [list, tuple, set]:
        return type(thing)([inspect(e) for e in thing])

    # if thing is a dictionary
    # recursively call inspect on every value
    if type(thing) == dict:
        return {k:inspect(v) for k,v in thing.items()}

    try:
        # Assume thing is some weird object
        # call inspect on thing's __dict__ attribute
        # the above block will get called
        return inspect(thing.__dict__)
    except:
        # if thing is not a weird object,
        # thing is probably something simple like int, float, str etc
        # simply return thing
        return thing

def print_pretty(thing: Any):
    ins = inspect(thing)
    js = json.dumps(ins, indent=2)
    print(js)