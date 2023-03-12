from __future__ import annotations


class CustomTypeDefinition:
    def __init__(
        self,
        type_: type,
        name: str,
        fields: dict[str, str],
    ) -> None:
        self.type_ = type_
        self.name = name
        self.fields = fields

    @staticmethod
    def create(obj: object) -> CustomType:
        type_ = type(obj)
        name = type(obj).__name__
        fields = {key: "any" for key in vars(obj)}

        return CustomTypeDefinition(type_, name, fields)
