from pyteal import *
from fs import FileSystem

def test():
    fs = FileSystem()

    return Seq(
        Pop(fs.write(Int(0), Int(0), Bytes("deadbeef"*128))),
        Log(fs.read(Int(0), Int(0), Int(512))),
        Int(1)
    )

print(compileTeal(test(), mode=Mode.Application, version=5))
