from pyteal import *

pageSize = Int(127)


@Subroutine(TealType.bytes)
def intkey(i: TealType.uint64) -> Expr:
    return Extract(Itob(i), Int(7), Int(1))


@Subroutine(TealType.bytes)
def safeSub(b: TealType.bytes, start: TealType.uint64, stop: TealType.uint64) -> Expr:
    return (
        If(b == Bytes(""))
        .Then(Bytes(""))
        .ElseIf(Len(b) < stop)
        .Then(Substring(b, start, Len(b)))
        .Else(Substring(b, start, stop))
    )


@Subroutine(TealType.bytes)
def safeExtract(
    b: TealType.bytes, start: TealType.uint64, len: TealType.uint64
) -> Expr:
    return (
        If(start + len > Len(b))
        .Then(Extract(b, start, Len(b) - start))
        .Else(Extract(b, start, len))
    )


@Subroutine(TealType.bytes)
def safeGet(idx: TealType.uint64, key: TealType.bytes) -> Expr:

    mv = App.localGetEx(idx, Int(0), key)
    return Seq(mv, If(mv.hasValue()).Then(mv.value()).Else(Bytes("")))


class FileSystem:
    def __init__(self):
        # Init with max size or specific k/vs to use ?
        # Do we even need a class or can these all
        pass

    @staticmethod
    @Subroutine(TealType.bytes)
    def read(
        idx: TealType.uint64, bstart: TealType.uint64, bstop: TealType.uint64
    ) -> Expr:

        startKey = bstart / pageSize
        startOffset = bstart % pageSize

        stopKey = bstop / pageSize
        stopOffset = bstop % pageSize

        key = ScratchVar()
        buff = ScratchVar()

        start = ScratchVar()
        stop = ScratchVar()
        work = ScratchVar()

        init = key.store(startKey)
        cond = key.load() <= stopKey
        incr = key.store(key.load() + Int(1))

        return Seq(
            buff.store(Bytes("")),
            For(init, cond, incr).Do(
                Seq(
                    start.store(If(key.load() == startKey, startOffset, Int(0))),
                    stop.store(If(key.load() == stopKey, stopOffset, pageSize)),
                    buff.store(
                        Concat(
                            buff.load(),
                            safeSub(
                                safeGet(idx, intkey(key.load())),
                                start.load(),
                                stop.load(),
                            ),
                        )
                    ),
                )
            ),
            buff.load(),
        )

    @staticmethod
    @Subroutine(TealType.uint64)
    def write(
        idx: TealType.uint64, bstart: TealType.uint64, buff: TealType.bytes
    ) -> Expr:

        stop = Len(buff)

        startKey = bstart / pageSize
        startOffset = bstart % pageSize

        stopKey = stop / pageSize
        stopOffset = stop % pageSize

        key = ScratchVar()
        page = ScratchVar()

        start = ScratchVar()
        stop = ScratchVar()

        written = ScratchVar()

        init = key.store(startKey)
        cond = key.load() <= stopKey
        incr = key.store(key.load() + Int(1))

        return Seq(
            written.store(Int(0)),
            For(init, cond, incr).Do(
                Seq(
                    start.store(If(key.load() == startKey, startOffset, Int(0))),
                    stop.store(If(key.load() == stopKey, stopOffset, pageSize)),
                    App.localPut(
                        idx,
                        intkey(key.load()),
                        If(stop.load() - start.load() < pageSize)  # Its a partial write
                        .Then(
                            Concat(
                                safeSub(
                                    safeGet(idx, intkey(key.load())),
                                    Int(0),
                                    start.load(),
                                ),
                                safeExtract(
                                    buff,
                                    written.load(),
                                    written.load() + (stop.load() - start.load()),
                                ),
                                safeSub(
                                    safeGet(idx, intkey(key.load())),
                                    stop.load(),
                                    pageSize,
                                ),
                            )
                        )
                        .Else(safeExtract(buff, written.load(), pageSize)),
                    ),
                    written.store(written.load() + (stop.load() - start.load())),
                )
            ),
            written.load(),
        )
