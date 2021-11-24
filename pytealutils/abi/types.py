from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Dict, List, Union
from inspect import signature
from functools import wraps
from Cryptodome.Hash import SHA512
from algosdk import abi
from pyteal import *


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


__package__ = "abi"
