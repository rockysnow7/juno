import struct

from typing import Any
from data import Data, RefData, BoolData, IntData, FloatData, StringData, ListData


DATA_TYPES_INTS = {
    RefData: 0,
    BoolData: 1,
    IntData: 2,
    FloatData: 3,
    StringData: 4,
    ListData: 5,
}
DATA_TYPE_BYTES = 2 # 2 bytes = 65,536 possible data types
NUMBER_VALUE_BYTES = 8 # 8 bytes = i64/f64 numbers, u64 refs


class Store:
    def __init__(self) -> None:
        self.__entities = {}

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
        raise TypeError(f"object is of the invalid type '{type(obj).__name__}'")

    def __obj_from_Data(self, data: Data) -> Any:
        if isinstance(data, RefData):
            referee_bytes = self.__entities[data.value]
            referee_data = self.__Data_from_bytes(referee_bytes)
            referee_obj = self.__obj_from_Data(referee_data)
            return referee_obj

        if isinstance(data, BoolData) \
        or isinstance(data, IntData) \
        or isinstance(data, FloatData) \
        or isinstance(data, StringData):
            return data.value

        if isinstance(data, ListData):
            items = [self.__obj_from_Data(item) for item in data.value]
            return items
        raise NotImplementedError(f"obj method for datatype '{type(data).__name__}' not implemented")

    def __Data_as_bytes(self, data: Data) -> bytes:
        data_bytes = DATA_TYPES_INTS[type(data)].to_bytes(DATA_TYPE_BYTES, signed=False)

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
            item_len = NUMBER_VALUE_BYTES + DATA_TYPE_BYTES
            items_bytes = [value_bytes[i:i + item_len] for i in range(0, len(value_bytes), item_len)]
            items = [self.__Data_from_bytes(b) for b in items_bytes]
            return ListData(items)
        raise NotImplementedError(f"from_bytes method for byte {type_int} not implemented")

    def store(self, obj: Any) -> int:
        obj_data = self.__obj_as_Data(obj)
        obj_bytes = self.__Data_as_bytes(obj_data)
        obj_id = len(self.__entities)
        self.__entities[obj_id] = obj_bytes

        return obj_id

    def get(self, id_: int) -> Data:
        return self.__obj_from_Data(self.__Data_from_bytes(id_.to_bytes(NUMBER_VALUE_BYTES, signed=False)))

    def print_entities(self) -> None:
        print(self.__entities)
