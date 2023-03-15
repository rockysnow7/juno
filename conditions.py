from typing import Callable, Any


CONDITION_RETURN_TYPE = Callable[[Any], bool]


def is_type(type_: type) -> CONDITION_RETURN_TYPE:
    return lambda obj: isinstance(obj, type_)

def has_field(field: str, value: Any) -> CONDITION_RETURN_TYPE:
    return lambda obj: getattr(obj, field) == value
