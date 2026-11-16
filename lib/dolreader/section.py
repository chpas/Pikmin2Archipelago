from io import BytesIO
from typing import Union

class Section(object):

    class SectionType:
        TEXT = 0
        DATA = 1
        UNDEFINED = -1

    def __init__(self, address: int = None, data: Union[bytes, bytearray, BytesIO] = BytesIO()):
        self.address = address

        if isinstance(data, (bytes, bytearray)):
            self.data = BytesIO(data)
        elif isinstance(data, BytesIO):
            self.data = data
        else:
            raise TypeError(f"Data of type {data.__class__} is not valid. Use bytes, bytearray, or BytesIO")

    @property
    def size(self) -> int:
        return len(self.data.getbuffer())

    @property
    def id(self) -> int:
        return Section.SectionType.UNDEFINED


class TextSection(Section):

    def __init__(self, address: int = None, data: Union[bytes, bytearray, BytesIO] = BytesIO(), offset: int = None):
        super().__init__(address, data)
        self.offset = offset

    @property
    def id(self) -> int:
        return Section.SectionType.TEXT


class DataSection(Section):

    def __init__(self, address: int = None, data: Union[bytes, bytearray, BytesIO] = BytesIO(), offset: int = None):
        super().__init__(address, data)
        self.offset = offset

    @property
    def id(self) -> int:
        return Section.SectionType.DATA