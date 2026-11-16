from __future__ import annotations

import struct
from io import BytesIO, IOBase
from typing import BinaryIO, Iterable, List, Tuple, Union

from dolreader.exceptions import (AddressOutOfRangeError,
                                  IncompleteSectionError,
                                  SectionCountFullError, UnmappedAddressError)
from dolreader.section import DataSection, Section, TextSection


def read_sbyte(f):
    return struct.unpack("b", f.read(1))[0]

def write_sbyte(f, val):
    f.write(struct.pack("b", val))

def read_sint16(f):
    return struct.unpack(">h", f.read(2))[0]

def write_sint16(f, val):
    f.write(struct.pack(">h", val))

def read_sint32(f):
    return struct.unpack(">i", f.read(4))[0]

def write_sint32(f, val):
    f.write(struct.pack(">i", val))

def read_ubyte(f):
    return struct.unpack("B", f.read(1))[0]

def write_ubyte(f, val):
    f.write(struct.pack("B", val))

def read_uint16(f):
    return struct.unpack(">H", f.read(2))[0]

def write_uint16(f, val):
    f.write(struct.pack(">H", val))

def read_uint32(f):
    return struct.unpack(">I", f.read(4))[0]

def write_uint32(f, val):
    f.write(struct.pack(">I", val))

def read_float(f):
    return struct.unpack(">f", f.read(4))[0]

def write_float(f, val):
    f.write(struct.pack(">f", val))

def read_double(f):
    return struct.unpack(">d", f.read(4))[0]

def write_double(f, val):
    f.write(struct.pack(">d", val))

def read_bool(f, vSize=1):
    return struct.unpack("B", f.read(vSize))[0] > 0

def write_bool(f, val, vSize=1):
    f.write(b'\x00'*(vSize-1) + b'\x01') if val is True else f.write(b'\x00' * vSize)


class DolFile(object):
    MaxTextSections = 7
    MaxDataSections = 11
    OffsetInfoLoc = 0
    AddressInfoLoc = 0x48
    SizeInfoLoc = 0x90 
    BssInfoLoc = 0xD8
    EntryInfoLoc = 0xE0

    def __init__(self, stream: BinaryIO = None, startpos: int = 0):
        self.textSections: List[TextSection] = []
        self.dataSections: List[DataSection] = []

        self.bssAddress = 0
        self.bssSize = 0
        self.entryPoint = 0x80003000

        if stream is None: return
        
        # Read text and data section addresses and sizes 
        for i in range(DolFile.MaxTextSections + DolFile.MaxDataSections):
            stream.seek(DolFile.OffsetInfoLoc + (i << 2) + startpos)
            offset = read_uint32(stream)
            stream.seek(DolFile.AddressInfoLoc + (i << 2) + startpos)
            address = read_uint32(stream)
            stream.seek(DolFile.SizeInfoLoc + (i << 2) + startpos)
            size = read_uint32(stream)
            
            if offset >= 0x100:
                stream.seek(offset + startpos)
                data = BytesIO(stream.read(size))
                if i < DolFile.MaxTextSections:
                    self.textSections.append(TextSection(address=address, data=data, offset=offset))
                else:
                    self.dataSections.append(DataSection(address=address, data=data, offset=offset))
        
        stream.seek(DolFile.BssInfoLoc + startpos)
        self.bssAddress = read_uint32(stream)
        self.bssSize = read_uint32(stream)

        stream.seek(DolFile.EntryInfoLoc + startpos)
        self.entryPoint = read_uint32(stream)
        
        self._currLogicAddr = self.firstSection.address
        self.seek(self._currLogicAddr)
        stream.seek(0)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"

    def __str__(self) -> str:
        return f"Nintendo DOL executable"
        
    def resolve_address(self, gcAddr: int) -> Union[DataSection, TextSection]:
        """ Returns the data of the section that houses the given address\n
            UnmappedAddressError is raised when the address is unmapped """

        for section in self.sections:
            if section.address <= gcAddr < (section.address + section.size):
                return section
        
        raise UnmappedAddressError(f"Unmapped address: 0x{gcAddr:X}")

    def seek_nearest_unmapped(self, gcAddr: int, buffer: int = 0) -> int:
        '''Returns the nearest unmapped address (greater) if the given address is already taken by data'''

        for section in self.sections:
            if section.address > (gcAddr + buffer) or (section.address + section.size) < gcAddr:
                continue
            gcAddr = section.address + section.size

            try:
                self.resolve_address(gcAddr)
            except UnmappedAddressError:
                break
        return gcAddr

    @property
    def sections(self) -> Iterable[Union[DataSection, TextSection]]:
        """ Generator that yields each section's data """

        for i in self.textSections:
            yield i
        for i in self.dataSections:
            yield i

    @property
    def lastSection(self) -> Union[DataSection, TextSection]:
        return sorted(self.sections, key=lambda x: x.offset)[-1]

    @property
    def firstSection(self) -> Union[DataSection, TextSection]:
        return sorted(self.sections, key=lambda x: x.offset)[0]

    @property
    def size(self) -> int:
        try:
            section = self.lastSection
            return section.offset + section.size
        except IndexError:
            return 0x100
    
    def read(self, _size: int) -> bytes:
        section = self.resolve_address(self._currLogicAddr)
        if self._currLogicAddr + _size > (section.address + section.size):
            raise UnmappedAddressError("Read goes over current section")
            
        self._currLogicAddr += _size  
        return section.data.read(_size)
        
    def write(self, _data: bytes):
        section = self.resolve_address(self._currLogicAddr)
        if self._currLogicAddr + len(_data) > (section.address + section.size):
            raise UnmappedAddressError("Write goes over current section")
            
        section.data.write(_data)
        self._currLogicAddr += len(_data)
    
    def seek(self, where: int, whence: int = 0):
        if whence == 0:
            section = self.resolve_address(where)
            section.data.seek(where - section.address)
            
            self._currLogicAddr = where
        elif whence == 1:
            section = self.resolve_address(self._currLogicAddr + where)
            section.data.seek((self._currLogicAddr + where) - section.address)
            
            self._currLogicAddr += where
        else:
            raise NotImplementedError(f"Unsupported whence type '{whence}'")
        
    def tell(self) -> int:
        return self._currLogicAddr
    
    def save(self, stream: BinaryIO, startpos: int = 0):
        stream.seek(startpos)
        stream.write(b"\x00" * self.size)

        for i, section in enumerate(self.sections):
            if section.id == Section.SectionType.TEXT:
                entry = i
            elif section.id == Section.SectionType.DATA:
                entry = i + (DolFile.MaxTextSections - len(self.textSections))
            else:
                raise IncompleteSectionError(f"Section {i} is abstract, convert to DataSection or TextSection for saving")

            stream.seek(DolFile.OffsetInfoLoc + (entry << 2) + startpos)
            write_uint32(stream, section.offset) #offset in file
            stream.seek(DolFile.AddressInfoLoc + (entry << 2) + startpos)
            write_uint32(stream, section.address) #game address
            stream.seek(DolFile.SizeInfoLoc + (entry << 2) + startpos)
            write_uint32(stream, section.size) #size in file

            stream.seek(section.offset + startpos)
            stream.write(section.data.getbuffer())

        stream.seek(DolFile.BssInfoLoc + startpos)
        write_uint32(stream, self.bssAddress)
        write_uint32(stream, self.bssSize)

        stream.seek(DolFile.EntryInfoLoc + startpos)
        write_uint32(stream, self.entryPoint)
        stream.seek(startpos)

    def is_mapped(self, address: int) -> bool:
        try:
            self.resolve_address(address)
            return True
        except UnmappedAddressError:
            return False

    def get_section_size(self, index: int, _type: Section.SectionType) -> int:
        """ Return the current size of the specified section\n
            section: DolFile.SectionType """

        if _type == Section.SectionType.TEXT:
            return self.textSections[index].size
        elif _type == Section.SectionType.DATA:
            return self.dataSections[index].size
    
    def append_section(self, section: Union[TextSection, DataSection]):
        if section.id == Section.SectionType.TEXT:
            if len(self.textSections) >= DolFile.MaxTextSections:
                raise SectionCountFullError(f"Exceeded max text section limit of {DolFile.MaxTextSections}")

            prevSection = self.textSections[-1]
        elif section.id == Section.SectionType.DATA:
            if len(self.dataSections) >= DolFile.MaxDataSections:
                raise SectionCountFullError(f"Exceeded max data section limit of {DolFile.MaxTextSections}")

            prevSection = self.dataSections[-1]
        else:
            raise IncompleteSectionError(f"Section is incomplete, convert to DataSection or TextSection nefore attaching to a DOL")

        finalSection = self.lastSection

        if section.address is None:
            section.address = self.seek_nearest_unmapped(prevSection.address + prevSection.size, (section.size + 31) & -32)
        if section.offset is None:
            section.offset = finalSection.offset + finalSection.size
        
        section.offset = (section.offset + 31) & -32

        if section.address < 0x80000000 or section.address >= 0x81200000:
            raise AddressOutOfRangeError(f"Address '{section.address:08X}' of this {section.__class__} is beyond scope (0x80000000 <-> 0x81200000)")

        if section.id == Section.SectionType.TEXT:
            self.textSections.append(section)
        else:
            self.dataSections.append(section)

    def insert_branch(self, to: int, _from: int, lk: bool = False):
        """ Insert a branch instruction at `_from`\n
            to:    address to branch to\n
            _from: address to branch from\n
            lk:    is branch linking? """

        _from &= 0xFFFFFFFC
        to &= 0xFFFFFFFC
        self.seek(_from)
        write_uint32(self, (to - _from) & 0x3FFFFFD | 0x48000000 | (1 if lk else 0))

    def extract_branch_addr(self, bAddr: int) -> Tuple[int, bool]:
        """ Returns the destination of the given branch,
            and if the branch is conditional """

        self.seek(bAddr)

        ppc = read_uint32(self)
        conditional = (ppc >> 24) & 0xFF < 0x48

        if conditional is True:
            if (ppc & 0x8000):
                offset = (ppc & 0xFFFD) - 0x10000
            else:
                offset = ppc & 0xFFFD
        else:
            if (ppc & 0x2000000):
                offset = (ppc & 0x3FFFFFD) - 0x4000000
            else:
                offset = ppc & 0x3FFFFFD

        return (bAddr + offset, conditional)

    def read_sbyte(self, address: int):
        self.seek(address)
        return struct.unpack("b", self.read(1))[0]

    def write_sbyte(self, address: int, val: int):
        self.seek(address)
        self.write(struct.pack("b", val))

    def read_sint16(self, address: int):
        self.seek(address)
        return struct.unpack(">h", self.read(2))[0]

    def write_sint16(self, address: int, val: int):
        self.seek(address)
        self.write(struct.pack(">h", val))

    def read_sint32(self, address: int):
        self.seek(address)
        return struct.unpack(">i", self.read(4))[0]

    def write_sint32(self, address: int, val: int):
        self.seek(address)
        self.write(struct.pack(">i", val))

    def read_ubyte(self, address: int):
        self.seek(address)
        return struct.unpack("B", self.read(1))[0]

    def write_ubyte(self, address: int, val: int):
        self.seek(address)
        self.write(struct.pack("B", val))

    def read_uint16(self, address: int):
        self.seek(address)
        return struct.unpack(">H", self.read(2))[0]

    def write_uint16(self, address: int, val: int):
        self.seek(address)
        self.write(struct.pack(">H", val))

    def read_uint32(self, address: int):
        self.seek(address)
        return struct.unpack(">I", self.read(4))[0]

    def write_uint32(self, address: int, val: int):
        self.seek(address)
        self.write(struct.pack(">I", val))

    def read_float(self, address: int):
        self.seek(address)
        return struct.unpack(">f", self.read(4))[0]

    def write_float(self, address: int, val: float):
        self.seek(address)
        self.write(struct.pack(">f", val))

    def read_double(self, address: int):
        self.seek(address)
        return struct.unpack(">d", self.read(4))[0]

    def write_double(self, address: int, val: float):
        self.seek(address)
        self.write(struct.pack(">d", val))

    def read_bool(self, address: int, vSize=1):
        self.seek(address)
        return struct.unpack("B", self.read(vSize))[0] > 0

    def write_bool(self, address: int, val, vSize=1):
        self.seek(address)
        self.write(b'\x00'*(vSize-1) + b'\x01') if val is True else self.write(b'\x00' * vSize)

    def read_c_string(self, address: int, maxlen: int = 0, encoding: str = "ascii") -> str:
        """ Reads a null terminated string from the specified address """
        self.seek(address)

        length = 0
        string = ""
        while (char := self.read(1)) != b"\x00":
            try:
                string += char.decode(encoding)
                length += 1
            except UnicodeDecodeError:
                print(f"{char} at pos {length}, (address 0x{address + length:08X}) is not a valid {encoding} character")
                return string[:-1]
            if length > (maxlen-1) and maxlen != 0:
                return string

        return string

    def read_string(self, address: int, strlen: int, encoding: str = "ascii") -> str:
        """ Reads a string of `strlen` bytes from the specified address """
        self.seek(address)
        return self.read(strlen).decode(encoding)

    def write_string(self, address: int, string: str, encoding: str = "ascii"):
        """ Writes a string to the specified address """
        self.seek(address)
        self.write(string.encode(encoding) + b"\x00")

    def print_info(self):
        print("")
        print("|-- DOL INFO --|".center(20, " "))
        print("")

        for i, section in enumerate(self.textSections):
            header = f"|  Text section {i}  |"
            info = [ "-"*len(header) + "\n" + header + "\n" + "-"*len(header), 
                     "File Offset:".ljust(16, " ") + f"0x{section.offset:X}", 
                     "Virtual addr:".ljust(16, " ") + f"0x{section.address:X}",
                     "Size:".ljust(16, " ") + f"0x{section.size:X}" ]
                     
            print("\n".join(info) + "\n")
        
        for i, section in enumerate(self.dataSections):
            header = f"|  Data section {i}  |"
            info = [ "-"*len(header) + "\n" + header + "\n" + "-"*len(header), 
                     "File Offset:".ljust(16, " ") + f"0x{section.offset:X}", 
                     "Virtual addr:".ljust(16, " ") + f"0x{section.address:X}",
                     "Size:".ljust(16, " ") + f"0x{section.size:X}" ]

            print("\n".join(info) + "\n")

        header = "|  BSS section  |"  
        info = [ "-"*len(header) + "\n" + header + "\n" + "-"*len(header),
                 "Virtual addr:".ljust(16, " ") + f"0x{self.bssAddress:X}",
                 "Size:".ljust(16, " ") + f"0x{self.bssSize:X}",
                 "End:".ljust(16, " ") + f"0x{self.bssAddress+self.bssSize:X}" ]

        print("\n".join(info) + "\n")
        
        header = "|  Miscellaneous Info  |"
        info = [ "-"*len(header) + "\n" + header + "\n" + "-"*len(header),
                 "Text sections:".ljust(16, " ") + f"0x{len(self.textSections):X}",
                 "Data sections:".ljust(16, " ") + f"0x{len(self.dataSections):X}",
                 "File length:".ljust(16, " ") + f"0x{self.size:X}" ]

        print("\n".join(info) + "\n")

if __name__ == "__main__":
    # Example usage (Reading global string "mario" from Super Mario Sunshine (NTSC-U))

    with open("Start.dol", "rb") as f:
        dol = DolFile(f)
        
    name = dol.read_c_string(0x804165A0)
    print(name)
