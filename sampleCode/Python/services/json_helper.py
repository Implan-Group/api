import json
import logging

from typing import Any, Type, TypeVar

T = TypeVar('T')


class JsonHelper:

    @staticmethod
    def serialize(value: Any) -> str:
        json_str = json.dumps(value, indent=4, separators=(',', ': '))
        return json_str

    @staticmethod
    def deserialize(json_str: str, cls: Type[T]) -> T | None:
        cls_dict = json.loads(json_str)
        try:
            instance: T = cls(**cls_dict)
        except Exception as ex:
            logging.error(f"Could not Deserialize Json into {cls}: {ex}")
            raise
        return instance