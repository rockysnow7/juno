from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod


DATA_TYPES_INTS = {
    "RefData": 0,
    "BoolData": 1,
    "IntData": 2,
    "ListData": 3,
}


class Data(ABC):
    @abstractmethod
    def __init__(self, value) -> None:
        pass

class RefData(Data):
    def __init__(self, value: int) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"RefData({self.value})"

class BoolData(Data):
    def __init__(self, value: bool) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"BoolData({self.value})"

class IntData(Data):
    def __init__(self, value: int) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"IntData({self.value})"

class FloatData(Data):
    def __init__(self, value: float) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"FloatData({self.value})"

class StringData(Data):
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"StringData(\"{self.value}\")"

class ListData(Data):
    def __init__(self, value: list[Any]) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"ListData({self.value})"

class DictData(Data):
    def __init__(self, value: dict[any, any]) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"DictData({self.value})"

class CustomData(Data):
    def __init__(self, type_name: str, fields: list[Data]) -> None:
        self.type_name = type_name
        self.fields = fields

    @staticmethod
    def from_obj(obj: object) -> CustomData:
        type_name = type(obj).__name__
        fields = list(vars(obj).values())

        return CustomData(type_name, fields)
