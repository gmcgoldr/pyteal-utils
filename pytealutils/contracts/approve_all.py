from pyteal import Subroutine, Expr, TealType, Approve
from application import Application


class ApproveAll(Application):
    @staticmethod
    @Subroutine(TealType.uint64)
    def create() -> Expr:
        return Approve()

    @staticmethod
    @Subroutine(TealType.uint64)
    def update() -> Expr:
        return Approve()

    @staticmethod
    @Subroutine(TealType.uint64)
    def delete() -> Expr:
        return Approve()

    @staticmethod
    @Subroutine(TealType.uint64)
    def optIn() -> Expr:
        return Approve()

    @staticmethod
    @Subroutine(TealType.uint64)
    def closeOut() -> Expr:
        return Approve()

    @staticmethod
    @Subroutine(TealType.uint64)
    def clearState() -> Expr:
        return Approve()
