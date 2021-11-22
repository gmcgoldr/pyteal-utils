from pyteal import *


@Subroutine(TealType.anytype)
def must_get(v: TealType.bytes) -> Expr:
    maybe = (App.globalGet(0, v),)
    return Seq(maybe, Assert(maybe.hasValue()), maybe.value())


@Subroutine(TealType.anytype)
def default_get(v: TealType.bytes, d: Expr) -> Expr:
    maybe = (App.globalGet(0, v),)
    return Seq(
        maybe,
        If(maybe.hasValue(), maybe.value(), d),
    )
