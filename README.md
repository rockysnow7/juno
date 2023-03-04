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
