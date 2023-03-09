# store

definitions:

```
define type Person {
    name!: string,
    age: number,
    children?: list of Person,
};
```

actions:

```
save Person {
    name: "John Smith",
    age: 28,
};
save Person {
    name: "Tom Smith",
    age: 4,
};

edit Person with name "John Smith" {
    children: [Person with name "Tom Smith"],
};
```

Python examples:

```python
from dido import Store

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

bob = Person("Bob", 21)
store = Store()
store.save(bob)

del bob

bob = store.get({
    "type": Person,
    "name": "Bob",
})[0]
print(bob.name) # => "Bob"

store.edit({
    "type": Person,
    "name": "Bob",
}, {
    "age": 22,
})
```