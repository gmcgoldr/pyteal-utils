from pyteal import ScratchVar, Int, For, Seq, Expr, TealType, Subroutine


@Subroutine(TealType.none)
def range(n: TealType.uint64, method: Expr):
    i = ScratchVar()

    init = i.store(0)
    cond = init.load() < n
    iter = init.Store(init.Load() + Int(1))

    return Seq(init.Store(0), For(init, cond, iter).Do(method), Int(1))
