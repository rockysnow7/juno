import os
import struct
import conditions

from typing import Any, Callable
from dataclasses import dataclass
from pathlib import Path
from data import Data, RefData, BoolData, IntData, FloatData, StringData, ListData, DictData, CustomData


PRIMITIVE_TYPES = {bool, int, float, str, list, dict}

DATA_TYPES_INTS = {
    RefData: 0,
    BoolData: 1,
    IntData: 2,
    FloatData: 3,
    StringData: 4,
    ListData: 5,
    DictData: 6,
    CustomData: 7,
}
DATA_TYPE_BYTES = 1
CUSTOM_DATA_TYPE_BYTES = 2 # 2 bytes = 65,536 possible custom data types
NUMBER_VALUE_BYTES = 8 # 8 bytes = i64/f64 numbers, u64 refs


@dataclass
class CustomTypeData:
    type: type
    primary_fields: list[str]

class Store:
    def __init__(
        self,
        custom_types: list[type] = [],
        custom_types_primary_fields: dict[str, list[str]] = {},
    ) -> None:
        Path(".juno/entities").mkdir(parents=True, exist_ok=True)
        Path(".juno/custom_types").mkdir(exist_ok=True)

        entity_ids = [int(id_name, 16) for id_name in os.listdir(".juno/entities")]
        self.__current_max_entity_id = max(entity_ids) if entity_ids else -1
        type_ids = [int(id_name, 16) for id_name in os.listdir(".juno/custom_types")]
        self.__current_max_type_id = max(type_ids) if type_ids else -1

        self.__custom_types = {}
        for type_ in custom_types:
            if self.__get_custom_type_id_by_name(type_.__name__) is None:
                self.__define_custom_type(
                    type_,
                    custom_types_primary_fields.get(type_.__name__, []),
                )
            else:
                type_id = self.__get_custom_type_id_by_name(type_.__name__)
                primary_fields = self.__get_custom_type_primary_fields(type_id)
                self.__custom_types[type_.__name__] = CustomTypeData(type_, primary_fields)

    def __get_entity_bytes(self, id_: int) -> bytes:
        id_name = hex(id_)[2:]
        with open(f".juno/entities/{id_name}", "rb") as f:
            entity_bytes = f.read()
        return entity_bytes

    def __save_entity_bytes(
        self,
        entity_bytes: bytes,
        id_: int | None = None,
    ) -> None:
        if id_ is None:
            self.__current_max_entity_id += 1
            id_name = hex(self.__current_max_entity_id)[2:]
        else:
            id_name = hex(id_)[2:]

        with open(f".juno/entities/{id_name}", "wb+") as f:
            f.write(entity_bytes)

    def __get_custom_type_data(self, id_: int) -> dict[str, str | list[str]]:
        id_name = hex(id_)[2:]
        with open(f".juno/custom_types/{id_name}", "rb") as f:
            data_id_bytes = f.read()
        data_id = int.from_bytes(data_id_bytes)

        return self.get_by_id(data_id)

    def __get_custom_type_name(self, id_: int) -> str:
        return self.__get_custom_type_data(id_)["name"]

    def __get_custom_type_primary_fields(self, id_: int) -> list[str]:
        return self.__get_custom_type_data(id_)["primary_fields"]

    def __get_custom_type_id_by_name(self, name: str) -> int | None:
        for id_name in os.listdir(".juno/custom_types"):
            id_ = int(id_name, 16)
            if self.__get_custom_type_name(id_) == name:
                return int(id_name, 16)

    def __define_custom_type(
        self,
        type_: type,
        primary_fields: list[str],
    ) -> None:
        self.__current_max_type_id += 1
        id_name = hex(self.__current_max_type_id)[2:]

        type_data = {
            "name": type_.__name__,
            "primary_fields": primary_fields,
        }
        type_data_id = self.store(type_data)
        type_data_id_bytes = type_data_id.to_bytes(NUMBER_VALUE_BYTES, signed=False)

        with open(f".juno/custom_types/{id_name}", "wb+") as f:
            f.write(type_data_id_bytes)
        self.__custom_types[type_.__name__] = CustomTypeData(type_, primary_fields)

    def __obj_as_Data(self, obj: Any) -> Data:
        if isinstance(obj, bool):
            return BoolData(obj)
        if isinstance(obj, int):
            return IntData(obj)
        if isinstance(obj, float):
            return FloatData(obj)
        if isinstance(obj, str):
            return StringData(obj)
        if isinstance(obj, list):
            return ListData(obj)
        if isinstance(obj, dict):
            return DictData(obj)

        return CustomData.from_obj(obj)

    def __obj_from_Data(self, data: Data) -> Any:
        if isinstance(data, RefData):
            referee_bytes = self.__get_entity_bytes(data.value)
            referee_data = self.__Data_from_bytes(referee_bytes)
            referee_obj = self.__obj_from_Data(referee_data)
            return referee_obj

        if isinstance(data, BoolData) \
        or isinstance(data, IntData) \
        or isinstance(data, FloatData) \
        or isinstance(data, StringData) \
        or isinstance(data, DictData):
            return data.value

        if isinstance(data, ListData):
            items = [self.__obj_from_Data(item) for item in data.value]
            return items

        if isinstance(data, CustomData):
            obj = self.__custom_types[data.type_name].type(*data.fields)
            return obj
        raise NotImplementedError(f"obj method for datatype '{type(data).__name__}' not implemented")

    def __Data_as_bytes(self, data: Data) -> bytes:
        data_type_int = DATA_TYPES_INTS[type(data)]
        data_bytes = data_type_int.to_bytes(DATA_TYPE_BYTES, signed=False)

        if isinstance(data, RefData):
            data_bytes += data.value.to_bytes(NUMBER_VALUE_BYTES, signed=False)
            return data_bytes

        if isinstance(data, BoolData):
            data_bytes += bytes([int(data.value)])
            return data_bytes

        if isinstance(data, IntData):
            data_bytes += data.value.to_bytes(NUMBER_VALUE_BYTES, signed=True)
            return data_bytes

        if isinstance(data, FloatData):
            value_bytes = bytearray(NUMBER_VALUE_BYTES)
            struct.pack_into("d", value_bytes, 0, data.value)
            data_bytes += bytes(value_bytes)
            return data_bytes

        if isinstance(data, StringData):
            value_bytes = data.value.encode("utf-16")
            data_bytes += value_bytes
            return data_bytes

        if isinstance(data, ListData):
            for item in data.value:
                item_id = self.store(item)
                item_ref = RefData(item_id)
                item_ref_bytes = self.__Data_as_bytes(item_ref)
                data_bytes += item_ref_bytes
            return data_bytes

        if isinstance(data, DictData):
            pairs_list = [[key, value] for key, value in data.value.items()]
            pairs_list_id = self.store(pairs_list)
            pairs_list_ref = RefData(pairs_list_id)
            pairs_list_ref_bytes = self.__Data_as_bytes(pairs_list_ref)
            data_bytes += pairs_list_ref_bytes
            return data_bytes

        if isinstance(data, CustomData):
            type_id = self.__get_custom_type_id_by_name(data.type_name)
            type_id_bytes = type_id.to_bytes(CUSTOM_DATA_TYPE_BYTES, signed=False)
            data_bytes += type_id_bytes

            fields_list_id = self.store(data.fields)
            fields_list_ref = RefData(fields_list_id)
            fields_list_ref_bytes = self.__Data_as_bytes(fields_list_ref)
            data_bytes += fields_list_ref_bytes

            return data_bytes
        raise NotImplementedError(f"as_bytes method for datatype '{type(data).__name__}' not implemented")

    def __Data_from_bytes(self, b: bytes) -> Data:
        type_int = int.from_bytes(b[:DATA_TYPE_BYTES])
        value_bytes = b[DATA_TYPE_BYTES:]

        if type_int == DATA_TYPES_INTS[RefData]:
            return RefData(int.from_bytes(value_bytes))

        if type_int == DATA_TYPES_INTS[BoolData]:
            return BoolData(bool(value_bytes[0]))

        if type_int == DATA_TYPES_INTS[IntData]:
            return IntData(int.from_bytes(value_bytes))

        if type_int == DATA_TYPES_INTS[FloatData]:
            return FloatData(struct.unpack("d", value_bytes)[0])

        if type_int == DATA_TYPES_INTS[StringData]:
            return StringData(value_bytes.decode("utf-16"))

        if type_int == DATA_TYPES_INTS[ListData]:
            item_len = DATA_TYPE_BYTES + NUMBER_VALUE_BYTES
            items_bytes = [value_bytes[i:i + item_len] for i in range(0, len(value_bytes), item_len)]
            items = [self.__Data_from_bytes(b) for b in items_bytes]
            return ListData(items)

        if type_int == DATA_TYPES_INTS[DictData]:
            pairs_list_ref = self.__Data_from_bytes(value_bytes)
            pairs_list = self.get_by_id(pairs_list_ref.value)
            d = {key: value for key, value in pairs_list}
            return DictData(d)

        if type_int == DATA_TYPES_INTS[CustomData]:
            custom_type_bytes = value_bytes[:CUSTOM_DATA_TYPE_BYTES]
            custom_type_int = int.from_bytes(custom_type_bytes)
            custom_type_name = self.__get_custom_type_name(custom_type_int)

            fields_list_ref_bytes = value_bytes[CUSTOM_DATA_TYPE_BYTES:]
            fields_list_ref = self.__Data_from_bytes(fields_list_ref_bytes)
            fields_list = self.get_by_id(fields_list_ref.value)

            return CustomData(custom_type_name, fields_list)
        raise NotImplementedError(f"from_bytes method for byte {type_int} not implemented")

    def __show(
        self,
        obj: Any,
        child: bool = False,
        *,
        base_indent_len: int = 0,
    ) -> str:
        base_indent = " " * base_indent_len
        indent = " " * 4

        if isinstance(obj, bool) \
        or isinstance(obj, int) \
        or isinstance(obj, float):
            return base_indent + str(obj)

        if isinstance(obj, str):
            return base_indent + f"\"{obj}\""

        if isinstance(obj, list):
            if child:
                return base_indent + "<list>"

            children = [self.__show(c, True) for c in obj[:3]]
            return base_indent + f"[{', '.join(children)}{', ...' if len(obj) > 3 else ''}]"

        if isinstance(obj, dict):
            if child:
                return base_indent + "<dict>"

            keys = []
            values = []
            for key, value in list(obj.items())[:3]:
                keys.append(self.__show(key, True))
                values.append(self.__show(value, True))

            s = "{\n"
            for key, value in zip(keys, values):
                s += base_indent + indent + f"{key}: {value},\n"

            if len(obj) > 3:
                s += base_indent + indent + "...\n"
            s += base_indent + "}"

            return s

        if child:
            return base_indent + f"<{type(obj).__name__} object>"

        name = type(obj).__name__
        content = self.__show(
            vars(obj),
            base_indent_len=base_indent_len,
        ).strip()
        return base_indent + name + " " + content

    def store(self, obj: Any, id_: int = None) -> int:
        if type(obj) not in PRIMITIVE_TYPES and id_ is None:
            type_name = type(obj).__name__
            type_id = self.__get_custom_type_id_by_name(type_name)
            type_primary_fields = self.__get_custom_type_primary_fields(type_id)

            if type_primary_fields:
                conditions_ = [conditions.is_type(type(obj))]
                for field in type_primary_fields:
                    condition = conditions.has_field(field, getattr(obj, field))
                    conditions_.append(condition)
                objs = self.get_all(conditions_)

                if objs:
                    mes = f"there already exists a {type_name} object with these primary field values, namely:\n\n"
                    mes += self.__show(objs[0], base_indent_len=4)

                    raise ValueError(mes)

        obj_data = self.__obj_as_Data(obj)
        obj_bytes = self.__Data_as_bytes(obj_data)
        self.__save_entity_bytes(obj_bytes, id_)

        return self.__current_max_entity_id

    def get_by_id(self, id_: int) -> Any:
        id_bytes = id_.to_bytes(NUMBER_VALUE_BYTES, signed=False)
        data = self.__Data_from_bytes(id_bytes)
        return self.__obj_from_Data(data)

    def get_all(self, conditions_: list[Callable[[Any], bool]]) -> list[Any]:
        if not conditions_:
            return []

        objs = []
        for id_name in os.listdir(".juno/entities"):
            id_ = int(id_name, 16)
            obj = self.get_by_id(id_)

            valid = True
            for condition in conditions_:
                if not condition(obj):
                    valid = False
                    break

            if valid:
                objs.append(obj)
        return objs

    def get_the(self, conditions_: list[Callable[[Any], bool]]) -> Any:
        objs = self.get_all(conditions_)
        if len(objs) == 0:
            raise KeyError("no object with these conditions exists")
        if len(objs) > 1:
            raise KeyError(f"multiple ({len(objs)}) objects with these conditions exist")

        return objs[0]
