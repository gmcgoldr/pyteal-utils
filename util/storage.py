from pyteal import Subroutine, TealType, MaybeValue, Expr, Assert, Seq, If

@Subroutine(TealType.anytype)
def must_get(v: MaybeValue) -> Expr:
    return Seq(v, Assert(v.hasValue()), v.value())

@Subroutine(TealType.anytype)
def default_get(v: MaybeValue, d: Expr) -> Expr:
    return Seq(v, If(v.hasValue(), v.value(), d))
