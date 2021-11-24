from pyteal import *
from application import ApproveAll, Application, ABIMethod
import json

from sys import path
from os.path import dirname, abspath

path.append(dirname(abspath(__file__)) + "/..")
import abi


class Calculator(ApproveAll):
    @staticmethod
    @ABIMethod(abi.Uint32)
    def add(a: abi.Uint32, b: abi.Uint32) -> Expr:
        return a + b

    @staticmethod
    @ABIMethod(abi.Uint32)
    def sub(a: abi.Uint32, b: abi.Uint32) -> Expr:
        return a - b

    @staticmethod
    @ABIMethod(abi.Uint32)
    def div(a: abi.Uint32, b: abi.Uint32) -> Expr:
        return a / b

    @staticmethod
    @ABIMethod(abi.Uint32)
    def mul(a: abi.Uint32, b: abi.Uint32) -> Expr:
        return a * b

app = Calculator()

with open("interface.json", "w") as f:
    f.write(json.dumps(app.get_interface().dictify()))

with open("approval.teal", "w") as f:
    f.write(compileTeal(app.handler(), mode=Mode.Application, version=5))
