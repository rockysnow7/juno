from store import Store


#class Person:
#    def __init__(self, name: str) -> None:
#        self.name = name
#
#bob = Person("Bob")
store = Store()
id_ = store.store({
    "hey": [1, 2],
})

print(id_, store.get(id_))
