from enum import Enum
from typing import Any, Type, TypeVar, Optional
from pydantic import BaseModel, json
from pydantic.json import pydantic_encoder

T = TypeVar('T')

class CamelCaseModel(BaseModel):
    class Config:
        alias_generator = lambda field: ''.join(word.capitalize() if i else word for i, word in enumerate(field.split('_')))
        allow_population_by_field_name = True
        json_encoders = {
            Enum: lambda e: e.value,
        }

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

class Json:
    @staticmethod
    def serialize(obj: Any) -> str:
        """Serialize the given object using the standard JSON serializer."""
        return json.dumps(obj, default=pydantic_encoder, indent=4, separators=(',', ': '))

    @staticmethod
    def deserialize(json_str: str, cls: Type[T]) -> Optional[T]:
        """Deserialize the given JSON string into an object of type T."""
        if json_str is None:
            return None
        return cls.parse_raw(json_str)

