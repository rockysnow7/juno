# store

definitions:

```
define type Person {
    name: string,
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
```