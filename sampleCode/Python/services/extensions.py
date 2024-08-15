from typing import TypeVar, Optional

T = TypeVar('T')

class ArgumentNullException(Exception):
    pass

class Extensions:
    @staticmethod
    def throw_if_null(value: Optional[T], value_name: Optional[str] = None) -> T:
        if value is not None:
            return value
        raise ArgumentNullException(f'Argument "{value_name}" is null.')

    @staticmethod
    def is_null_or_whitespace(s: Optional[str]) -> bool:
        return s is None or s.strip() == ''


