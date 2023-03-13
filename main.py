from person import Person, Gender
from store import Store


tom = Person("Tom Smith", Gender("male"), 4, [])
john = Person("John Smith", Gender("male"), 28, [tom])

store = Store()
store.store(john)

a = store.get_all([
    lambda obj: isinstance(obj, Person),
    lambda obj: obj.name == "Tom Smith",
])
print(a)
