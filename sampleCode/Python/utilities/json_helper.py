import json
import humps

from datetime import datetime, date
from enum import Enum
from typing import Any, Type, TypeVar
from uuid import UUID


class CustomJSONEncoder(json.JSONEncoder):
    """
    A customized JSONEncoder that can handle additional types
    """
    def default(self, obj:Any) -> Any:
        # Enums we convert into their underlying value
        # This accounts for the way we use Enums to access the Api
        if isinstance(obj, Enum):
            return obj.value
        # Dates/Times need conversion
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        # UUID (guid) needs converted directly into a string
        elif isinstance(obj, UUID):
            return str(obj)
        # Anything that looks like a dictionary needs sub-processing
        elif hasattr(obj, '__dict__'):
            # For custom objects, apply the same transformation logic
            return JsonHelper._convert_to_dict(obj)
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
    def _convert_to_dict(value: Any) -> dict:
        """
        Converts a value into a dict, excluding None values, with Pascalized Names
        """

        # Convert into a dict using vars (keys will be field names, values will be field values)
        value_dict: dict = vars(value)
        # Remove all pairs where the value is None
        clean_dict: dict = {key: value for key, value in value_dict.items() if value is not None}
        # Use the humps library to convert from `lower_snake_case` field names into `PascalCase`
        renamed_dict: dict = humps.pascalize(clean_dict)
        # Now this dict corresponds to the API
        return renamed_dict

    @staticmethod
    def serialize(value: Any) -> str:
        """
        Serializes `value` into a json string representation
        :param value: The class object to convert
        :returns: A json string
        """

        # Convert to dict
        value_dict: dict = JsonHelper._convert_to_dict(value)

        # Transform the dict into a compact json string
        # We need to use a custom encoder
        json_str: str = json.dumps(value_dict,
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