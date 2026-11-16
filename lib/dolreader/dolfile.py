from __future__ import annotations

import struct
from io import BytesIO, IOBase

from dolreader.exceptions import (AddressOutOfRangeError, IncompleteSectionError,
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

def get_alignment(number, align: int):
    if number % align != 0:
        return align - (number % align)
    else:
        return 0

def stream_size(obj, ofs: int = 0) -> int:
    if hasattr(obj, "getbuffer"):
        return len(obj.getbuffer()) + ofs
    elif hasattr(obj, "tell") and hasattr(obj, "seek"):
        _pos = obj.tell()
        obj.seek(0, 2)
        _size = obj.tell()
        obj.seek(_pos, 1)
        return _size + ofs
    else:
        raise NotImplementedError(f"Getting the stream size of class {type(obj)} is unsupported")

def align_byte_size(obj, alignment: int, fillchar="00"):
    if isinstance(obj, bytes):
        obj += bytes.fromhex(fillchar * get_alignment(len(obj), alignment))
    elif isinstance(obj, bytearray):
        obj.append(bytearray.fromhex(fillchar * get_alignment(len(obj), alignment)))
    elif issubclass(type(obj), IOBase):
        _size = stream_size(obj)
        obj.write(bytes.fromhex(fillchar * get_alignment(_size, alignment)))
    else:
        raise NotImplementedError(f"Aligning the size of class {type(obj)} is unsupported")
    

class DolFile(object):

    maxTextSections = 7
    maxDataSections = 11
    offsetInfoLoc = 0
    addressInfoLoc = 0x48
    sizeInfoLoc = 0x90 
    bssInfoLoc = 0xD8
    entryInfoLoc = 0xE0

    def __init__(self, stream = None, startpos: int = 0):
        self.textSections = []
        self.dataSections = []

        self.bssAddress = None
        self.bssSize = None
        self.entryPoint = 0x80003000

        if stream is None: return
        
        # Read text and data section addresses and sizes 
        for i in range(DolFile.maxTextSections + DolFile.maxDataSections):
            stream.seek(DolFile.offsetInfoLoc + (i << 2) + startpos)
            offset = read_uint32(stream)
            stream.seek(DolFile.addressInfoLoc + (i << 2) + startpos)
            address = read_uint32(stream)
            stream.seek(DolFile.sizeInfoLoc + (i << 2) + startpos)
            size = read_uint32(stream)
            
            if offset >= 0x100:
                stream.seek(offset + startpos)
                data = BytesIO(stream.read(size))
                if i < DolFile.maxTextSections:
                    self.textSections.append(TextSection(address=address, data=data, offset=offset))
                else:
                    self.dataSections.append(DataSection(address=address, data=data, offset=offset))
        
        stream.seek(DolFile.bssInfoLoc + startpos)
        self.bssAddress = read_uint32(stream)
        self.bssSize = read_uint32(stream)

        stream.seek(DolFile.entryInfoLoc + startpos)
        self.entryPoint = read_uint32(stream)
        
        self._currLogicAddr = self.firstSection.address
        self.seek(self._currLogicAddr)
        stream.seek(0)

    def __repr__(self) -> str:
        return f"repr={vars(self)}"

    def __str__(self) -> str:
        return f"Nintendo DOL executable {self.__repr__()}"
        
    def resolve_address(self, gcAddr: int) -> [DataSection, TextSection]:
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
    def sections(self) -> [DataSection, TextSection]:
        """ Generator that yields each section's data """

        for i in self.textSections:
            yield i
        for i in self.dataSections:
            yield i

    @property
    def lastSection(self) -> [DataSection, TextSection]:
        return sorted(self.sections, key=lambda x: x.offset, reverse=True)[0]

    @property
    def firstSection(self) -> [DataSection, TextSection]:
        return sorted(self.sections, key=lambda x: x.offset)[0]

    @property
    def size(self) -> int:
        try:
            section = self.lastSection
            return (section.offset + section.size + 255) & -256
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
    
    def save(self, stream):
        stream.seek(0)
        stream.write(b"\x00" * self.size)

        for i, section in enumerate(self.sections):
            if section.id == Section.SectionType.TEXT:
                entry = i
            elif section.id == Section.SectionType.DATA:
                entry = i + (DolFile.maxTextSections - len(self.textSections))
            else:
                raise IncompleteSectionError(f"Section {i} is incomplete, convert to DataSection or TextSection for saving")

            stream.seek(DolFile.offsetInfoLoc + (entry << 2))
            write_uint32(stream, section.offset) #offset in file
            stream.seek(DolFile.addressInfoLoc + (entry << 2))
            write_uint32(stream, section.address) #game address
            stream.seek(DolFile.sizeInfoLoc + (entry << 2))
            write_uint32(stream, section.size) #size in file

            stream.seek(section.offset)
            stream.write(section.data.getbuffer())

        stream.seek(DolFile.bssInfoLoc)
        write_uint32(stream, self.bssAddress)
        write_uint32(stream, self.bssSize)

        stream.seek(DolFile.entryInfoLoc)
        write_uint32(stream, self.entryPoint)
        align_byte_size(stream, 256)


    def get_section_size(self, index: int, _type: Section.SectionType) -> int:
        """ Return the current size of the specified section\n
            section: DolFile.SectionType """

        if _type == Section.SectionType.TEXT:
            return self.textSections[index].size
        elif _type == Section.SectionType.DATA:
            return self.dataSections[index].size
    
    def append_section(self, section: [TextSection, DataSection]):
        if section.id == Section.SectionType.TEXT:
            if len(self.textSections) >= DolFile.maxTextSections:
                raise SectionCountFullError(f"Exceeded max text section limit of {DolFile.maxTextSections}")

            prevSection = self.textSections[-1]
        elif section.id == Section.SectionType.DATA:
            if len(self.dataSections) >= DolFile.maxDataSections:
                raise SectionCountFullError(f"Exceeded max data section limit of {DolFile.maxTextSections}")

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

    def append_data_sections(self, sectionsList: list):
        """ Follows the list format: [tuple(<Bytes>Data, <Int>GameAddress or None), tuple(<Bytes>Data... """

        for i, dataSet in enumerate(sectionsList):
            if len(self.dataSections) >= DolFile.maxDataSections:
                raise SectionCountFullError(f"Exceeded max data section limit of {DolFile.maxDataSections}")

            finalSection = self.lastSection
            lastSection = self.dataSections[len(self.dataSections) - 1]
            data, address = dataSet

            if not hasattr(data, "getbuffer"):
                if hasattr(data, "read"):
                    data.seek(0)
                    data = BytesIO(data.read())
                else:
                    data = BytesIO(data)

            offset = finalSection.offset + finalSection.size

            if i < len(sectionsList) - 1:
                size = (len(data.getbuffer()) + 31) & -32
            else:
                size = (len(data.getbuffer()) + 255) & -256

            if address is None:
                address = self.seek_nearest_unmapped(lastSection.address + lastSection.size, size)

            if address < 0x80000000 or address >= 0x81200000:
                raise AddressOutOfRangeError(f"Address '{address:08X}' of data section {i} is beyond scope (0x80000000 <-> 0x81200000)")

            self.dataSections.append({"offset": offset, "address": address, "size": size, "data": data, "type": Section.SectionType.DATA})

    def insert_branch(self, to: int, _from: int, lk: bool = False):
        """ Insert a branch instruction at _from\n
            to:    address to branch to\n
            _from: address to branch from\n
            lk:    0 | 1, is branch linking? """

        _from &= 0xFFFFFFFC
        to &= 0xFFFFFFFC
        self.seek(_from)
        write_uint32(self, (to - _from) & 0x3FFFFFD | 0x48000000 | 1 if lk else 0)

    def extract_branch_addr(self, bAddr: int) -> tuple:
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

    def read_string(self, addr: int, maxlen: int = 0, encoding: str = "ascii") -> str:
        """ Reads a null terminated string from the specified address """
        self.seek(addr)

        length = 0
        string = ""
        while (char := self.read(1)) != b"\x00":
            try:
                string += char.decode(encoding)
                length += 1
            except UnicodeDecodeError:
                print(f"{char} at pos {length}, (address 0x{addr + length:08X}) is not a valid {encoding} character")
                return string[:-1]
            if length > (maxlen-1) and maxlen != 0:
                return string

        return string

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
        
    name = dol.read_string(0x804165A0)
    print(name)
