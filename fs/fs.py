from pyteal import *

pageSize = Int(127)

class FileSystem:


    def __init__():
        pass

    @Subroutine(TealType.bytes)
    def read(idx: TealType.uint64, bstart: TealType.uint64, bstop:TealType.uint64) -> Expr:

        startKey    = bstart / pageSize
        startOffset = bstart % pageSize

        stopKey    = bstop / pageSize
        stopOffset = bstop % pageSize

        key   = ScratchVar()
        buff  = ScratchVar()

        start = ScratchVar()
        stop  = ScratchVar()

        init = key.store(startKey)
        cond = key.load() < stopKey
        incr = key.store(key.load() + Int(1))

        return Seq(
            b.store("")
            For(init, cond, incr).Do(
                start.store(If(key.load() == startKey.load(), startOffset, Int(0)))
                stop.store(If(key.load() == stopKey.load(), stopOffset, pageSize))
                b.store(Concat(
                    b.load(),
                    Substr(App.localGet(idx, key.load(),start.load(), stop.load())
                ))
            ),

            b.load()
        )

    @Subroutine(TealType.uint64)
    def write(idx: TealType.uint64, bstart: TealType.uint64, buff:TealType.bytes) -> Expr:


        stop = Len(buff)

        startKey    = bstart / pageSize
        startOffset = bstart % pageSize

        stopKey    = stop / pageSize
        stopOffset = stop % pageSize

        key   = ScratchVar()
        page  = ScratchVar()

        start = ScratchVar()
        stop  = ScratchVar()

        written = ScratchVar()

        init = key.store(startKey)
        cond = key.load() < stopKey
        incr = key.store(key.load() + Int(1))

        return Seq(
            written.store(0)
            For(init, cond, incr).Do(
                start.store(If(key.load() == startKey.load(), startOffset, Int(0)))
                stop.store(If(key.load() == stopKey.load(), stopOffset, pageSize))

                App.LocalPut(idx, key.load(),
                    If(stop.load() - start.load()<pageSize) # Its a partial write
                    .Then(
                        Concat(
                            Substr(App.localGet(idx, key.load()), 0, start.load()),
                            Substr(buff, written.load(), written.load() + (stop.load()-start.load())),
                            Substr(App.localGet(idx, key.load()), stop.load(), pageSize)
                        )
                    )
                    .Else(Substr(buff, written.load(), pageSize))
                )

                written.store(written.load() + (stop.load() - start.load()))
            ),
            written.load()
        )
