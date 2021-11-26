from abc import ABC, abstractmethod
from typing import List, Tuple, TypeVar, Generic, Union
from pyteal import *

@Subroutine(TealType.bytes)
def prepend_length(v: TealType.bytes) -> Expr:
    return Concat(Uint16.encode(Len(v)), v)

@Subroutine(TealType.bytes)
def remove_length(v: TealType.bytes) -> Expr:
    return Extract(v, Int(2), Uint16.decode(v))

@Subroutine(TealType.bytes)
def tuple_get_bytes(b: TealType.bytes, idx: TealType.uint64)->Expr:
    pos = ScratchVar()
    return Seq(
        pos.store(ExtractUint16(b, idx * Int(2))), # Get the position in the byte array
        Extract(
            b, 
            pos.load() + Int(2),  # start after the uint16 length bytes
            ExtractUint16(b, pos.load()) #until the end of the length
        )
    )

@Subroutine(TealType.bytes)
def tuple_get_address(b: TealType.bytes, idx: TealType.uint64)->Expr:
    pos = ScratchVar()
    return Seq(
        pos.store(ExtractUint16(b, idx * Int(2))), # Get the position in the byte array
        Extract(b, pos.load(), Int(32))
    )

@Subroutine(TealType.bytes)
def tuple_get_int(b: TealType.bytes, size: TealType.uint64, idx: TealType.uint64)->Expr:
    pos = ScratchVar()
    return Seq(
        pos.store(ExtractUint16(b, idx * Int(2))), # Get the position in the byte array
        Extract(b, pos.load(), Extract(b, pos.load(), size/Int(8)))
    )

@Subroutine(TealType.bytes)
def tuple_add_bytes(data: TealType.bytes, length: TealType.uint64, b: TealType.bytes)->Expr:
    idx = ScratchVar(TealType.uint64)
    init = idx.store(Int(0))
    cond = idx.load()<length
    iter = idx.store(idx.load() + Int(1))

    buff = ScratchVar(TealType.bytes)

    return Seq(
        buff.store(Bytes("")),
        For(init, cond, iter).Do(
            buff.store(
                Concat(
                    buff.load(),
                    Uint16.encode(ExtractUint16(data, idx.load()*Int(2)) + Int(2))
                )
            )
        ),
        Concat(
            buff.load(),

            #Set position of new data
            Uint16.encode(Len(data)+Int(2)),

            #Add existing bytes back
            Substring(data, length*Int(2), Len(data)),

            # Add bytes prefixed with length
            Uint16.encode(Len(b)), b
        )
    )

@Subroutine(TealType.bytes)
def tuple_add_address(a: TealType.bytes, b: TealType.bytes):
    pass

@Subroutine(TealType.bytes)
def tuple_add_int(a: TealType.bytes, b: TealType.bytes):
    pass

def abiTypeName(t)->str:
    if hasattr(t, "__name__"):
        return t.__name__.lower()
    elif t.__origin__ is DynamicArray:
        return "{}[]".format(abiTypeName(t.__args__[0]))
    elif t.__origin__ is FixedArray:
        return "{}[{}]".format(abiTypeName(t.__args__[0]), t.__args__[1])
    elif t.__origin__ is Tuple:
        return "({})".format(",".join([abiTypeName(a) for a in t.__args__]))

    return ""


class ABIType(ABC):
    @abstractmethod
    def decode() -> Expr:
        pass

    @abstractmethod
    def encode() -> Expr:
        pass

class Uint64(ABIType):
    stack_type = TealType.uint64

    @staticmethod
    @Subroutine(TealType.uint64)
    def decode(value: Bytes) -> Expr:
        return Btoi(value)

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Int) -> Expr:
        return Itob(value)


class Uint32(ABIType):
    stack_type = TealType.uint64

    @staticmethod
    @Subroutine(TealType.uint64)
    def decode(value: Bytes) -> Expr:
        return ExtractUint32(value, Int(0))

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Int) -> Expr:
        return Extract(Itob(value), Int(4), Int(4))


class Uint16(ABIType):
    stack_type = TealType.uint64

    @staticmethod
    @Subroutine(TealType.uint64)
    def decode(value: Bytes) -> Expr:
        return ExtractUint16(value, Int(0))

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Int) -> Expr:
        return Extract(Itob(value), Int(6), Int(2))

class String(ABIType):
    stack_type = TealType.bytes

    @staticmethod
    @Subroutine(TealType.bytes)
    def decode(value: Bytes) -> Expr:
        return remove_length(value)

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: bytes) -> Expr:
        return prepend_length(value)

class Address(ABIType):
    stack_type = TealType.bytes

    @staticmethod
    @Subroutine(TealType.bytes)
    def decode(value: Bytes) -> Expr:
        return value

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: bytes) -> Expr:
        return value

T = TypeVar('T', bound=ABIType)


    
class FixedArray(Generic[T]):
    stack_type = TealType.bytes

    @staticmethod
    @Subroutine(TealType.bytes)
    def decode(value: Bytes) -> Expr:
        return value

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Bytes) -> Expr:
        return value

class DynamicArray(Generic[T]):

    stack_type = TealType.bytes

    len = ScratchVar(TealType.uint64)
    data = ScratchVar(TealType.bytes) 

    def wrap(self, data: TealType.bytes)->Expr:
        return Seq(
            self.len.store(ExtractUint16(data, Int(0))),
            self.data.store(Extract(data, Int(2), Len(data) - Int(2))),
        )

    def create(self)->Expr:
        return Seq(
            self.len.store(Int(0)),
            self.data.store(Bytes(""))
        )

    
    def __getitem__(self, idx: Union[Int, int]) -> T:
        if isinstance(idx, int):
            idx = Int(idx) 
        return self.get(idx)

    def get(self, idx: Int) -> T:
        if self.__orig_class__.__args__[0] is String:
            return tuple_get_bytes(self.data.load(), idx)
        elif self.__orig_class__.__args__[0] is Address:
            return tuple_get_address(self.data.load(), idx)
        else:
            return tuple_get_int(self.data.load(), Int(64), idx)

    def push(self, b: TealType.bytes):
        if self.__orig_class__.__args__[0] is String:
            return Seq(
                self.data.store(tuple_add_bytes(self.data.load(), self.len.load(), b)),
                self.len.store(self.len.load() + Int(1))
            )
        elif self.__orig_class__.__args__[0] is Address:
            return Assert(Int(0)) 
        else:
            return Assert(Int(0))

    def serialize(self) -> Bytes:
        return Concat(
            Uint16.encode(self.len.load()),
            self.data.load()
        )

    @staticmethod
    @Subroutine(TealType.bytes)
    def decode(value: Bytes) -> Expr:
        return value

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: TealType.bytes) -> Expr:
        return value 

class Tuple(Generic[T]):
    stack_type = TealType.bytes

    def __init__(self, types:List[ABIType]):
        pass

    # uint16 position of first element, uint16 position of next ... then types 
    @staticmethod
    @Subroutine(TealType.bytes)
    def decode(value: Bytes) -> Expr:
        pass

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Bytes) -> Expr:
        pass