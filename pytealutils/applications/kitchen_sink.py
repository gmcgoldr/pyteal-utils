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
        idx = ScratchVar()
        buff = ScratchVar()

        init = idx.store(Len(a))
        cond = idx.load() > Int(0)
        iter = idx.store(idx.load() - Int(1))

        return Seq(
            buff.store(Bytes("")),
            For(init, cond, iter).Do(
                buff.store(Concat(buff.load(), Extract(a, idx.load() - Int(1), Int(1))))
            ),
            buff.load(),
        )

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
