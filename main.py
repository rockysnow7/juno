import conditions

from person import Person, Gender
from store import Store


store = Store([Person, Gender], {
    "Person": ["name"],
})
store.store(Person("a", Gender("a"), 1, []))
store.store(Person("a", Gender("b"), 1, []))

a = store.get_all([
    conditions.is_type(Person),
    conditions.has_field("name", "a"),
])
print(a)
