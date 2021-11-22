from pyteal import *
from dataclasses import field
from typing import Annotated, List
from tealstruct import TealStruct

from dataclasses import dataclass

Address = Annotated[Bytes, 32]

zero_address = lambda: Bytes("00"*32)

@dataclass
class TestStruct(TealStruct):
    address: Address = field(default_factory=zero_address)
    balance: Int     = Int(0)

# Need TealType.* to be generic types?
#Address = Annotated[List[TealType.uint64], 32]

def application():
    t = TestStruct()
    print(t.address)
    print(dir(t.address))
    return Seq(
        t.init()(Concat(Bytes("FF"*32), Itob(Int(10)))),
        Log(t.address),
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
    application()
    #print(compileTeal(application(), mode=Mode.Application, version=5))
