from typing import Any
from store import Store


class Person:
    def __init__(self, name: str) -> None:
        self.name = name

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Person) and other.name == self.name

bob = Person("Bob")
store = Store()
id_ = store.store(bob)

recovered = store.get(id_)
print(bob.name)
print(recovered.name)
assert recovered == bob
