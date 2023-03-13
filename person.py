from __future__ import annotations
from typing import Any


class Gender:
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Gender(\"{self.value}\")"

    def __eq__(self, other: Any) -> bool:
        return other.value == self.value

class Person:
    def __init__(
        self,
        name: str,
        gender: Gender,
        age: int,
        children: list[Person],
    ) -> None:
        self.name = name
        self.gender = gender
        self.age = age
        self.children = children

    def __repr__(self) -> str:
        return f"Person(\"{self.name}\", {self.gender}, {self.age}, {self.children})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Person) \
        and other.name == self.name \
        and other.gender == self.gender \
        and other.age == self.age \
        and other.children == self.children
