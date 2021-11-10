from pyteal import *
from fs import FileSystem

def test():
    fs = FileSystem()

    test = Seq(
        Pop(fs.write(Int(0), Int(0), Bytes("deadbeef"*16))),
        Log(fs.read(Int(0), Int(8), Int(32))),
        Int(1)
    )
    return Cond(
        [Txn.application_id() == Int(0), Int(1)],
        [Txn.on_completion() == OnComplete.OptIn, Int(1)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(1)],
        [Int(1), test],
    )

print(compileTeal(test(), mode=Mode.Application, version=5))