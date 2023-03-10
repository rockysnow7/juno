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

class BoolData(Data):
    def __init__(self, value: bool) -> None:
        self.value = value

class IntData(Data):
    def __init__(self, value: int) -> None:
        self.value = value

class ListData(Data):
    def __init__(self, value: list[Any]) -> None:
        self.value = value
