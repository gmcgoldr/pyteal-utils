from pyteal import *
from typing import Annotated, List
from tealstruct import TealStruct

from dataclasses import dataclass

@dataclass
class TestStruct(TealStruct):
    name:       TealType.bytes  = Bytes("")
    balance:    TealType.uint64 = Int(0)
    address:    Annotated[List[str], 12] = List[str]

# Need TealType.* to be generic types?
#Address = Annotated[List[TealType.uint64], 32]

#@dataclass
#def BankAccount(Struct):
#    address: Address
#    balance: TealType.uint64
#    interest: TealType.uint64


def application():
    t = TestStruct()
    return Seq(
        t.init()(Bytes("Ben"), Int(10), "DEADBEEFDEAD"),
        Log(t.name()),
        Int(1),
    )

def application2():
    t = TestStruct(ScratchVar(TealType.bytes))
    t.get_fields()
    return Seq(
        t.put(Bytes("")),
        t.put(Bytes("")),
        t.put(Bytes("")),
        t.put(Bytes("")),
        t.put(Bytes("")),
        t.put(Bytes("")),
        Int(1),
    )
if __name__ == "__main__":
    print(compileTeal(application(), mode=Mode.Application, version=5))
