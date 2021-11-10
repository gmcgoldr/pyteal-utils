from pyteal import Subroutine, TealType, Exp, Int, Bytes


@Subroutine(TealType.uint64)
def ilog10(x: TealType.uint64):
    return Exp(Int(10), x)
