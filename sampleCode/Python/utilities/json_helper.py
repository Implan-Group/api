"""Translation between the API's JSON and the sample's Python models.

The Impact API speaks `camelCase`; Python is written in `snake_case`. These two
functions do the conversion, and `ApiModel` gives every model a tolerant
constructor so the samples keep working when the API starts returning a field they
have never heard of.

That tolerance is the important part. The API gains fields over time, and a model
that raises on an unexpected key turns a routine addition into a broken sample, so
unknown keys are kept in `extra` rather than rejected. Print `model.extra` when you
want to see everything a response really contained.
"""

import dataclasses
import enum
import re
import uuid
from typing import Any, Mapping, Self

# Matches the position just before an inner capital letter: the boundary between
# `hash` and `Id` in `hashId`.
_CAMEL_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def camel_case(name: str) -> str:
    """Convert a Python field name to the API's spelling: `hash_id` -> `hashId`."""
    head, *rest = name.split("_")
    return head + "".join(word[:1].upper() + word[1:] for word in rest)


def snake_case(name: str) -> str:
    """Convert an API field name to Python's spelling: `hashId` -> `hash_id`."""
    return _CAMEL_BOUNDARY.sub("_", name).lower()


def to_json_value(value: Any) -> Any:
    """Render one Python value the way the API expects to receive it.

    Enums become their string value, UUIDs become their text form, models become
    dictionaries, and collections are converted item by item.
    """
    if isinstance(value, ApiModel):
        return value.to_api()
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [to_json_value(item) for item in value]
    if isinstance(value, dict):
        return {camel_case(key): to_json_value(item) for key, item in value.items()}
    return value


@dataclasses.dataclass
class ApiModel:
    """Base class for every request and response model in the samples.

    Subclasses are plain dataclasses. This base adds `from_api`, which builds an
    instance from a JSON object without tripping over fields it does not know, and
    `to_api`, which turns an instance back into the JSON the API expects.
    """

    # Anything the API returned that this model does not declare. Nothing is
    # silently discarded: inspect `model.extra` to see what else came back.
    extra: dict[str, Any] = dataclasses.field(
        default_factory=dict, repr=False, compare=False, kw_only=True
    )

    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> Self:
        """Build a model from one JSON object, keeping unknown fields in `extra`."""
        known = {f.name for f in dataclasses.fields(cls) if f.name != "extra"}
        arguments: dict[str, Any] = {}
        extra: dict[str, Any] = {}

        for api_name, value in payload.items():
            python_name = snake_case(api_name)
            if python_name in known:
                arguments[python_name] = value
            else:
                # A field the API has added, or one this sample has no use for.
                # Keep it rather than failing.
                extra[api_name] = value

        return cls(**arguments, extra=extra)

    @classmethod
    def list_from_api(cls, payload: Any) -> list[Self]:
        """Build a list of models from a JSON array.

        Endpoints with nothing to return sometimes answer `null` rather than an
        empty array, so that case is treated as an empty list.
        """
        if not payload:
            return []
        return [cls.from_api(item) for item in payload]

    def to_api(self) -> dict[str, Any]:
        """Render this model as the JSON object the API expects.

        Fields set to `None` are left out rather than sent as `null`. The API reads
        an absent optional field as "not supplied", which is what `None` means in
        these models: a Group carries exactly one region identifier, and the other
        three stay absent.
        """
        result: dict[str, Any] = {}
        for field in dataclasses.fields(self):
            if field.name == "extra":
                continue
            value = getattr(self, field.name)
            if value is None:
                continue
            result[camel_case(field.name)] = to_json_value(value)
        return result
