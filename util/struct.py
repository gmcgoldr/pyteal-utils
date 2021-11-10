from pyteal import *
from typing import Tuple, Dict


class Struct:
    _data = ScratchVar(TealType.bytes)
    _conds = []

    def __init__(self, definition):
        pos = 0
        for field in definition:
            self._conds.append(
                [matches(Bytes(field[0])), [Int(pos), Int(field[1]), Int(field[2])]]
            )
            pos += field[1]

    def get_int(self):
        @Subroutine(TealType.uint64)
        def _getter(field: TealType.bytes):
            return Cond(
                *[
                    [cond[0](field), i64(self._data.load(), cond[1][0])]
                    for cond in self._conds
                ]
            )

        return _getter

    def get_bytes(self):
        @Subroutine(TealType.bytes)
        def _getter(field: TealType.bytes):
            return Cond(
                *[
                    [cond[0](field), sub(self._data.load(), cond[1][0], cond[1][1])]
                    for cond in self._conds
                ]
            )

        return _getter

    def store(self, data) -> Expr:
        return self._data.store(data)


@Subroutine(TealType.uint64)
def i64(d: TealType.bytes, s: TealType.uint64):
    return ExtractUint64(d, s)


@Subroutine(TealType.bytes)
def sub(d: TealType.bytes, s: TealType.uint64, l: TealType.uint64) -> Expr:
    return Substring(d, s, s + l)


def matches(fname):
    @Subroutine(TealType.uint64)
    def _impl(fcheck: TealType.bytes):
        return fcheck == fname

    return _impl
