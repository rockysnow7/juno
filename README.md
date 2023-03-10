# juno

juno is a highly abstracted object store with a query language, hera, and an
API.

## hera

Primitive types are `bool`, `int`, `float`, and `string`.
Reference types are `list` and any custom-defined types.

Custom types can be defined:

```
enum Gender {
    Male,
    Female,
    Other,
}

type Person {
    name!: string,
    gender: Gender,
    age: number,
    children?: list of Person,
}
```

Entities can be saved:

```
save Person {
    name: "John Smith",
    gender: Gender.Male,
    age: 28,
};
save Person {
    name: "Tom Smith",
    gender: Gender.Male,
    age: 4,
};
```

Entities can be fetched.
A `get all` query will return a list of all entities which meet the criteria.
A `get the` query will return the only entity which meets the criteria, or
will raise an error if it is possible for more than one entity to be returned.

```
get the Person with name "John Smith";
get all Person with gender Gender.Male;
```

Entities can be edited:

```
edit Person with name "John Smith" {
    children: [Person with name "Tom Smith"],
};
```

## Python API

```python
from juno import Store

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

bob = Person("Bob", 21)
store = Store()
store.save(bob)

recovered = store.get({
    "type": Person,
    "name": "Bob",
})[0]
assert bob == recovered

store.edit({
    "type": Person,
    "name": "Bob",
}, {
    "age": 22,
})
```
