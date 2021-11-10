from pyteal import *

pageSize = Int(127)

class FileSystem:


    def __init__(self):
        pass

    @staticmethod
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
            buff.store(Bytes("")),
            For(init, cond, incr).Do(
                Seq(
                    start.store(If(key.load() == startKey, startOffset, Int(0))),
                    stop.store(If(key.load() == stopKey, stopOffset, pageSize)),
                    buff.store(Concat(
                        buff.load(),
                        Substring(App.localGet(idx, key.load()),start.load(), stop.load())
                    ))
                )
            ),
            buff.load()
        )

    @staticmethod
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
            written.store(Int(0)),
            For(init, cond, incr).Do(
                Seq(
                    start.store(If(key.load() == startKey, startOffset, Int(0))),
                    stop.store(If(key.load() == stopKey, stopOffset, pageSize)),
                    App.localPut(idx, key.load(),
                        If(stop.load() - start.load()<pageSize) # Its a partial write
                        .Then(
                            Concat(
                                Substring(App.localGet(idx, key.load()), Int(0), start.load()),
                                Substring(buff, written.load(), written.load() + (stop.load()-start.load())),
                                Substring(App.localGet(idx, key.load()), stop.load(), pageSize)
                            )
                        )
                        .Else(Substring(buff, written.load(), pageSize))
                    ),
                    written.store(written.load() + (stop.load() - start.load()))
                )
            ),
            written.load()
        )
