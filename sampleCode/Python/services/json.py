# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
from enum import Enum
from typing import Any, Type, TypeVar, Optional
from pydantic import BaseModel
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

