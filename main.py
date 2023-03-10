from store import Store


store = Store()
id_ = store.store(["hey"])
store.print_entities()

print(id_, store.get(id_))
