from pyteal import *
from application import ABIMethod
from defaults import ApproveAll
import json


from sys import path
from os.path import dirname, abspath

path.append(dirname(abspath(__file__)) + "/..")
import abi


class KitchenSink(ApproveAll):
    @staticmethod
    @ABIMethod
    def reverse(a: abi.String) -> abi.String:
        @Subroutine(TealType.bytes)
        def reverse(a: TealType.bytes)->Expr:
            return If(Len(a)==Int(0)).Then(Bytes("")).Else(
                Concat(Extract(a, Len(a)-Int(1),Int(1)), reverse(Extract(a, Int(0), Len(a)-Int(1))))
            )

        return reverse(a)

    @staticmethod
    @ABIMethod
    def add(a: abi.Uint32, b: abi.Uint32) -> abi.Uint32:
        return a + b

    @staticmethod
    @ABIMethod
    def sub(a: abi.Uint32, b: abi.Uint32) -> abi.Uint32:
        return a - b

    @staticmethod
    @ABIMethod
    def div(a: abi.Uint32, b: abi.Uint32) -> abi.Uint32:
        return a / b

    @staticmethod
    @ABIMethod
    def mul(a: abi.Uint32, b: abi.Uint32) -> abi.Uint32:
        return a * b


if __name__ == "__main__":
    app = KitchenSink()

    with open("interface.json", "w") as f:
        f.write(json.dumps(app.get_interface().dictify()))

    with open("approval.teal", "w") as f:
        f.write(
            compileTeal(
                app.handler(), mode=Mode.Application, version=5, assembleConstants=True
            )
        )
