from abc import ABC, abstractmethod
from pyteal import *


# TODO: should be straight forward
# generalize uint stuff, use passed in arg to create encoder/decoders
# byte? get/set byte
# bool? get/set bit

# TODO: Not sure how to do these yet

# ufixed<N>x<M>: An N-bit unsigned fixed-point decimal number with precision M, where 8 <= N <= 512, N % 8 = 0, and 0 < M <= 160, which denotes a value v as v / (10^M).
# address: Used to represent a 32-byte Algorand address. This is equivalent to byte[32].
# <type>[<N>]: A fixed-length array of length N, where N >= 0. type can be any other type.
# <type>[]: A variable-length array. type can be any other type.
# (T1,T2,...,TN): A tuple of the types T1, T2, …, TN, N >= 0.


@Subroutine(TealType.bytes)
def prepend_length(v: TealType.bytes) -> Expr:
    return (Concat(Uint16.to_bytes(Len(v)), v),)


@Subroutine(TealType.bytes)
def remove_length(v: TealType.bytes) -> Expr:
    return Extract(v, Int(2), Uint16.from_bytes(v))


class ABIType(ABC):
    @abstractmethod
    def decode() -> Expr:
        pass

    @abstractmethod
    def encode() -> Expr:
        pass

    @abstractmethod
    def stack_type() -> Expr:
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

