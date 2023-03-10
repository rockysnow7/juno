from store import Store


store = Store()
id_ = store.store([True, [1, 2]])
#store.print_entities()

print(store.get(id_))
