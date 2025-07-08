import json
import humps

from datetime import datetime, date
from enum import Enum
from typing import Any, Type, TypeVar
from uuid import UUID


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj:Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return str(obj)
        # elif isinstance(obj, (list, tuple)):
        #     return [self.default(item) if not isinstance(item, (str, int, float, bool, type(None))) else item for item in obj]
        # elif isinstance(obj, dict):
        #     return {k: self.default(v) if not isinstance(v, (str, int, float, bool, type(None))) else v for k, v in obj.items()}
        elif hasattr(obj, '__dict__'):
            # For custom objects, apply the same transformation logic
            obj_dict = vars(obj)
            clean_dict = {k: v for k, v in obj_dict.items() if v is not None}
            return humps.pascalize(clean_dict)
        return super().default(obj)


class JsonHelper:
    """
    This is a static class that contains some methods to assist with translating json strings
    to and from specific `class` objects.
    The Implan Impact API follows json standards for 'camelCase' keys, but in Python,
    field names are in 'lower_snake_case'.
    These methods account for those differences.
    """

    @staticmethod
    def serialize(value: Any) -> str:
        """
        Serializes `value` into a json string representation
        :param value: The class object to convert
        :returns: A json string
        """

        # Convert the class to a dict, where the keys are the field names and the values are the field values
        value_dict: dict = vars(value)

        # Remove all pairs where the value is None
        clean_dict: dict = {k: v for k, v in value_dict.items() if v is not None}

        # Use Humps to transform the 'lower_snake_case' field names to 'PascalCase'
        renamed_dict: dict = humps.pascalize(clean_dict)

        # Transform the dict into a compact json string
        # We need a custom encoding to handle UUIDs
        json_str: str = json.dumps(renamed_dict,
                                   indent=None,
                                   separators=(',', ':'),
                                   cls=CustomJSONEncoder)

        return json_str

    @staticmethod
    def deserialize[T](content_bytes: bytes, cls: type[T]) -> T:
        """
        Deserialize json bytes into an Instance
        :param content_bytes: The json bytes
        :param cls: The Type of the class instance to return
        :returns: The new class instance
        """

        # Convert the json string into a json dict
        json_dict: dict = json.loads(content_bytes)

        # Use Humps to translate the 'camelCase' json keys to 'lower_snake_case' field names
        fixed_json_dict: dict = humps.decamelize(json_dict)

        # Use **kwargs to map the dict into a class instance
        instance = cls(**fixed_json_dict)
        return instance

    @staticmethod
    def deserialize_list[T](content_bytes: bytes, cls: type[T]) -> list[T]:
        """
        Deserialize json bytes into a list of Instances
        :param content_bytes: The json bytes
        :param cls: The Type of the class instance to return
        :returns: list[T]
        """

        instances: list[T] = []

        # Convert the content into json
        js = json.loads(content_bytes)

        # Special handling for Enums
        if issubclass(cls, Enum):
            # Convert each Str into its matching Enum
            value: str
            for value in js:
                try:
                    e: T = cls(value)
                    instances.append(e)
                except Exception as ex:
                    print(ex)
                    raise ex
            # Finished
            return instances

        # Non-Enum is likely a complex value

        # smart_hook = JsonHelper.smart_enum_decoder(EventType, strict_keys=False)

        # Use Humps to translate the 'camelCase' json keys to 'lower_snake_case' field names
        renamed_json: dict = humps.decamelize(js)

        # Use **kwargs to transform the json dict into cls instances
        instances = [cls(**k) for k in renamed_json]
        return instances