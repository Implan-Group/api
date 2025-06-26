import json
import logging

from typing import Any, Type, TypeVar

import humps

T = TypeVar('T')


class JsonHelper:

    @staticmethod
    def serialize(value: Any) -> str:
        json_str = json.dumps(value, indent=4, separators=(',', ': '))
        return json_str

    @staticmethod
    def deserialize(json_str: str, cls: Type[T]) -> T:
        # Convert the json string into a dictionary
        json_dict = json.loads(json_str)
        # Use Humps to translate the Pascal/Camel-cased property names to lower_snake
        json_dict_fixed = humps.decamelize(json_dict)
        # Use **kwargs to map the dict onto our class
        instance = cls(**json_dict_fixed)
        return instance

    @staticmethod
    def deserialize_list(json_str: str, cls: Type[T]) -> list[T]:
        # Convert the json string into a dictionary
        json_dict = json.loads(json_str)
        # Use Humps to translate the Pascal/Camel-cased property names to lower_snake
        json_dict_fixed = humps.decamelize(json_dict)
        # Use **kwargs to map the dict onto a list of our classes
        instances = [cls(**temp) for temp in json_dict_fixed]
        return instances