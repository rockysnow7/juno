from typing import Any
from data import Data, RefData, BoolData, IntData, ListData


DATA_TYPES_INTS = {
    RefData: 0,
    BoolData: 1,
    IntData: 2,
    ListData: 3,
}
INT_BYTES = 8 # 8 bytes = i64 ints, u64 refs


class Store:
    def __init__(self) -> None:
        self.__entities = {}

    def __obj_as_Data(self, obj: Any) -> Data:
        if isinstance(obj, bool):
            return BoolData(obj)
        if isinstance(obj, int):
            return IntData(obj)
        if isinstance(obj, list):
            return ListData(obj)
        raise TypeError(f"object is of the invalid type '{type(obj).__name__}'")

    def __obj_from_Data(self, data: Data) -> Any:
        if isinstance(data, RefData):
            referee_bytes = self.__entities[data.value]
            referee_data = self.__Data_from_bytes(referee_bytes)
            referee_obj = self.__obj_from_Data(referee_data)
            return referee_obj

        if isinstance(data, BoolData):
            return data.value

        if isinstance(data, IntData):
            return data.value

        if isinstance(data, ListData):
            items = [self.__obj_from_Data(item) for item in data.value]
            return items
        raise NotImplementedError(f"obj method for datatype '{type(data).__name__}' not implemented")

    def __Data_as_bytes(self, data: Data) -> bytes:
        data_bytes = bytes([DATA_TYPES_INTS[type(data)]])

        if isinstance(data, RefData):
            data_bytes += data.value.to_bytes(INT_BYTES, signed=False)
            return data_bytes

        if isinstance(data, BoolData):
            data_bytes += bytes([int(data.value)])
            return data_bytes

        if isinstance(data, IntData):
            data_bytes += data.value.to_bytes(INT_BYTES, signed=True)
            return data_bytes

        if isinstance(data, ListData):
            for item in data.value:
                print(f"{item=}")
                item_id = self.store(item)
                item_ref = RefData(item_id)
                item_ref_bytes = self.__Data_as_bytes(item_ref)
                data_bytes += item_ref_bytes
            return data_bytes
        raise NotImplementedError(f"as_bytes method for datatype '{type(data).__name__}' not implemented")

    def __Data_from_bytes(self, b: bytes) -> Data:
        type_byte = int(b[0])
        value_bytes = b[1:]

        if type_byte == DATA_TYPES_INTS[RefData]:
            return RefData(int.from_bytes(value_bytes))

        if type_byte == DATA_TYPES_INTS[BoolData]:
            return BoolData(bool(value_bytes[0]))

        if type_byte == DATA_TYPES_INTS[IntData]:
            return IntData(int.from_bytes(value_bytes))

        if type_byte == DATA_TYPES_INTS[ListData]:
            items_bytes = [value_bytes[i:i + INT_BYTES + 1] for i in range(0, len(value_bytes), INT_BYTES + 1)]
            items = [self.__Data_from_bytes(b) for b in items_bytes]
            return ListData(items)
        raise NotImplementedError(f"from_bytes method for byte {b[0]} not implemented")

    def store(self, obj: Any) -> int:
        obj_data = self.__obj_as_Data(obj)
        obj_bytes = self.__Data_as_bytes(obj_data)
        obj_id = len(self.__entities)
        self.__entities[obj_id] = obj_bytes

        return obj_id

    def get(self, id_: int) -> Data:
        return self.__obj_from_Data(self.__Data_from_bytes(id_.to_bytes(INT_BYTES, signed=False)))

    def print_entities(self) -> None:
        print(self.__entities)
