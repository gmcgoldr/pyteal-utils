from pyteal import Seq, Txn, compileTeal, Mode, Int, Bytes, For, Log, Itob, ScratchVar
from util.list import * 


demo_ints  = [10, 100, 1000, 100000, 100000000]
demo_bytes = b"".join([x.to_bytes(8,'big') for x in demo_ints])

def app():
    l = List(uint64)

    i = ScratchVar()
    init = i.store(Int(0))
    cond = i.load() < Int(len(demo_ints))
    iter = i.store(i.load() + Int(1))

    return Seq(
        l.set(Bytes(demo_bytes)),

        For(init, cond, iter).Do(
            Log(Itob(l[i.load()]))
        ),

        Int(1)
    )


if __name__ == "__main__":
    print(compileTeal(app(), Mode.Application, version=5))
