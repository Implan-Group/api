import json
import humps

from typing import Any, Type, TypeVar
from uuid import UUID

# Used for generic typing in deserialize
T = TypeVar('T')


class ExtendedJsonEncoder(json.JSONEncoder):
    """
    A custom JSONEncoder that handles special values
    """

    def default(self, obj):
        # If we have a UUID
        if isinstance(obj, UUID):
            # Just transform it into a string
            return str(obj)
        # Use the default transformation
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

        # Use Humps to transform the 'lower_snake_case' field names to 'camelCase'
        fixed_value_dict: dict = humps.camelize(value_dict)

        # Transform the dict into a compact json string
        # We need a custom encoding to handle UUIDs
        json_str: str = json.dumps(fixed_value_dict,
                                   indent=None,
                                   separators=(',', ':'),
                                   cls=ExtendedJsonEncoder)

        return json_str


    @staticmethod
    def deserialize(json_str: str, cls: Type[T]) -> T:
        """
        Deserialize a json string into a class instance
        :param json_str: The json string
        :param cls: The Type of the class instance to return
        :returns: The new class instance
        """

        # Convert the json string into a json dict
        json_dict: dict = json.loads(json_str)

        # Use Humps to translate the 'camelCase' json keys to 'lower_snake_case' field names
        fixed_json_dict: dict = humps.decamelize(json_dict)

        # Use **kwargs to map the dict into a class instance
        instance = cls(**fixed_json_dict)
        return instance

    @staticmethod
    def deserialize_list(json_str: str, cls: Type[T]) -> list[T]:
        """
        Deserialize a json string into a list of class instances
        :param json_str: The json string
        :param cls: The Type of the class instance to return
        :returns: list[T]
        """

        # Convert the json string into a json dict
        json_dict: dict = json.loads(json_str)

        # Use Humps to translate the 'camelCase' json keys to 'lower_snake_case' field names
        fixed_json_dict: dict = humps.decamelize(json_dict)

        # Use **kwargs to map the dict into a list of our classes
        instances = [cls(**value) for value in fixed_json_dict]
        return instances
