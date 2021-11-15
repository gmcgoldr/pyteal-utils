from pyteal import *
from typing import Tuple, Dict
from dataclasses import dataclass



@dataclass
class TealStruct:
    _data: ScratchVar = ScratchVar(TealType.bytes)
    #_conds: List[Tuple[Subroutine, Subroutine]]

    def __post_init__(self):
        #pos = 0
        for k,v in self.__dataclass_fields__.items():
            print(k)
            print(v.type)
            # create getter and setter for each field
            # use scratch var for start/length
            

    def init(self) -> Expr:
        @Subroutine(TealType.none)
        def _impl(data) -> Expr:
            return self._data.store(data)
        return _impl


    def _getbytesimpl(self, startvar, lengthvar) -> Expr:
        @Subroutine(TealType.none)
        def _impl(data):
            return Extract(self._data.load(), startvar.load(), lengthvar.load())
        return _impl

    def _getintimpl(self, startvar) -> Expr:
        @Subroutine(TealType.none)
        def _impl():
            return ExtractUint64(self._data.load(), startvar.load())
        return _impl

    def _putintimpl(self) -> Expr:
        @Subroutine(TealType.none)
        def _impl(data):
            return Seq([
                self._data.store(data)
            ]) 
        return _impl

    def _putbytesimpl(self) -> Expr:
        @Subroutine(TealType.none)
        def _impl(data):
            return Seq([
                self._data.store(data)
            ]) 
        return _impl


#for field in definition:
#    self._conds.append([
#        matches(Bytes(field[0])),
#        [Int(pos), Int(field[1]), Int(field[2])]
#    ])
#    pos += field[1]

#
#

#def matches(fname):
#    @Subroutine(TealType.uint64)
#    def _impl(fcheck: TealType.bytes):
#        return fcheck == fname
#    return _impl
