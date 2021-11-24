from pyteal import *
from application import ApproveAll, Application, ABIMethod

from sys import path
from os.path import dirname, abspath

path.append(dirname(abspath(__file__)) + "/..")
import abi


class MyApp(ApproveAll):
    @staticmethod
    @ABIMethod(abi.Uint32)
    def add(a: abi.Uint32, b: abi.Uint32) -> Expr:
        return a + b

    @staticmethod
    @ABIMethod(abi.Uint32)
    def subtract(a: abi.Uint32, b: abi.Uint32) -> Expr:
        return a - b


app = MyApp()
# print(app.get_interface())
compiled = compileTeal(MyApp().__teal__(), mode=Mode.Application, version=5)
with open("approval.teal", "w") as f:
    f.write(compiled)
