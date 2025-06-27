import json
from enum import Enum

import humps

from typing import Any, Type, TypeVar
from uuid import UUID

from models.enums import EventType

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

        smart_hook = JsonHelper.smart_enum_decoder(EventType, strict_keys=False)

        # Convert the json string into a json dict
        json_dict: dict = json.loads(json_str, object_hook=smart_hook)

        # Use Humps to translate the 'camelCase' json keys to 'lower_snake_case' field names
        fixed_json_dict: dict = humps.decamelize(json_dict)

        # Use **kwargs to map the dict into a list of our classes
        instances = [cls(**value) for value in fixed_json_dict]
        return instances

    E = TypeVar('E')

    @staticmethod
    def strings_to_enum(string_list: list[str], enum_class: Type[E]) -> list[E]:
        """
        Convert a list of strings to a list of enum values.

        Args:
            string_list:     List of string values to convert
            enum_class: The enum class to convert to

        Returns:
            List of enum values

        Raises:
            ValueError: If any string value is not a valid enum member
        """
        result = []
        for value in string_list:
            try:
                result.append(enum_class(value))
            except ValueError:
                raise ValueError(f"'{value}' is not a valid {enum_class.__name__} value")

        return result

    @staticmethod
    def smart_enum_decoder(*enum_classes: type[Enum], strict_keys: bool = False):
        """
        Advanced JSON decoder with multiple discovery strategies.

        Args:
            *enum_classes: Enum classes to use for conversion
            strict_keys: If True, only convert keys that match enum class names

        Returns:
            A function that can be used as object_hook in json.loads()
        """
        # Build mapping of enum class names to classes
        name_mapping = {}
        for enum_class in enum_classes:
            # Try multiple name variations
            class_name = enum_class.__name__.lower()
            name_mapping[class_name] = enum_class

            # Pluralized version
            plural_name = class_name + 's' if not class_name.endswith('s') else class_name
            name_mapping[plural_name] = enum_class

            # Without 'enum' suffix
            if class_name.endswith('enum'):
                base_name = class_name[:-4]
                name_mapping[base_name] = enum_class
                name_mapping[base_name + 's'] = enum_class

        def object_hook(obj: dict[str, Any]) -> dict[str, Any]:
            for key, value in obj.items():
                if isinstance(value, list) and all(isinstance(v, str) for v in value):
                    converted = False

                    if strict_keys:
                        # Only try conversion if key matches enum name
                        enum_class = name_mapping.get(key.lower())
                        if enum_class:
                            try:
                                obj[key] = JsonHelper.strings_to_enum(value, enum_class)
                                converted = True
                            except ValueError:
                                pass
                    else:
                        # First try key-based matching
                        enum_class = name_mapping.get(key.lower())
                        if enum_class:
                            try:
                                obj[key] = JsonHelper.strings_to_enum(value, enum_class)
                                converted = True
                            except ValueError:
                                pass

                        # If key-based matching failed, try all enums
                        if not converted:
                            for enum_class in enum_classes:
                                try:
                                    obj[key] = JsonHelper.strings_to_enum(value, enum_class)
                                    converted = True
                                    break
                                except ValueError:
                                    continue

            return obj

        return object_hook
