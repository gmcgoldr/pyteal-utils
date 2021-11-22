from pyteal import *
from application import Application, ABIMethod

class MyApp(Application):

    @staticmethod
    @Subroutine(TealType.uint64)
    def create()->Expr:
        return Approve() 

    @staticmethod
    @Subroutine(TealType.uint64)
    def update()->Expr:
        return Approve() 

    @staticmethod
    @Subroutine(TealType.uint64)
    def delete()->Expr:
        return Approve() 

    @staticmethod
    @Subroutine(TealType.uint64)
    def optIn()->Expr:
        return Approve() 

    @staticmethod
    @Subroutine(TealType.uint64)
    def closeOut()->Expr:
        return Approve() 

    @staticmethod
    @Subroutine(TealType.uint64)
    def clearState()->Expr:
        return Approve() 

    @staticmethod
    @ABIMethod(TealType.uint64)
    def add(a: TealType.uint64, b: TealType.uint64)->Expr:
        return a + b

    @staticmethod
    @ABIMethod(TealType.uint64)
    def subtract(a: TealType.uint64, b: TealType.uint64)->Expr:
        return a - b

print(compileTeal(MyApp().__expr__(), mode=Mode.Application, version=5))