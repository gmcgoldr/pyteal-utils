from abc import ABC, abstractmethod
from enum import Enum
from types import FunctionType
from typing import Callable, Dict, List, OrderedDict, Union
from inspect import signature
from functools import update_wrapper, wraps
from Cryptodome.Hash import SHA512
from algosdk import abi
from pyteal import *

from sys import path
from os.path import dirname, abspath

path.append(dirname(abspath(__file__)) + "/..")
import abi as tealabi


# Utility function to take the string version of a
# method signature and return the 4 byte selector
def hashy(method: str) -> Bytes:
    chksum = SHA512.new(truncate="256")
    chksum.update(method.encode())
    return Bytes(chksum.digest()[:4])


@Subroutine(TealType.none)
def ABIReturn(b: TealType.bytes) -> Expr:
    return Log(Concat(Bytes("base16", "0x151f7c75"), b))


def ABIMethod(func):
    sig = signature(func)
    returns = sig.return_annotation

    args = [v.annotation.__name__.lower() for v in sig.parameters.values()]
    method = "{}({}){}".format(func.__name__, ",".join(args), returns.__name__.lower())
    selector = hashy(method)

    setattr(func, "abi_signature", method)
    setattr(func, "abi_selector", selector)
    setattr(func, "abi_args", [abi.Argument(arg) for arg in args])
    setattr(func, "abi_returns", abi.Returns(returns.__name__.lower()))

    # Get the types specified in the method
    abi_codec = [v.annotation for v in sig.parameters.values()]

    # Replace signature with teal native types
    new_params = OrderedDict(
        [
            (k, v.replace(annotation=v.annotation.stack_type))
            for k, v in sig.parameters.items()
        ]
    )
    func.__signature__ = sig.replace(parameters=new_params.values())

    # Wrap with encode/decode
    @wraps(func)
    @Subroutine(TealType.uint64)
    def wrapper() -> Expr:
        # Invoke f with decoded arguments
        return Seq(
            ABIReturn(
                returns.encode(
                    func(
                        *[
                            abi_codec[idx].decode(Txn.application_args[idx + 1])
                            for idx in range(len(abi_codec))
                        ]
                    )
                )
            ),
            Int(1),
        )

    return wrapper


class Application(ABC):
    @abstractmethod
    def create(self) -> Expr:
        pass

    @abstractmethod
    def update(self) -> Expr:
        pass

    @abstractmethod
    def delete(self) -> Expr:
        pass

    @abstractmethod
    def optIn(self) -> Expr:
        pass

    @abstractmethod
    def closeOut(self) -> Expr:
        pass

    @abstractmethod
    def clearState(self) -> Expr:
        pass

    def get_methods(self) -> List[str]:
        base = [
            "get_methods",
            "get_interface",
            "get_contract",
            "handler",
            "clearState",
            "closeOut",
            "create",
            "delete",
            "optIn",
            "update",
        ]
        methods = []
        for m in dir(self):
            if m not in base and m[0] != "_":
                methods.append(m)

        return methods

    def get_interface(self) -> abi.Interface:
        abiMethods = []
        methods = self.get_methods()
        for method in methods:
            f = getattr(self, method)
            abiMethods.append(abi.Method(f.__name__, f.abi_args, f.abi_returns))

        # TODO: hacked this in for now, to provide extended extended budget
        abiMethods.append(abi.Method("pad", [], abi.Returns("void")))

        return abi.Interface(self.__class__.__name__, abiMethods)

    def get_contract(self, app_id: int) -> abi.Contract:
        interface = self.get_interface()
        return abi.Contract(interface.name, app_id, interface.methods)

    def handler(self) -> Expr:
        methods = self.get_methods()

        routes = [
            [Txn.application_args[0] == f.abi_selector, f()]
            for f in map(lambda m: getattr(self, m), methods)
        ]

        pad_selector = hashy("pad()void")
        routes.append([Txn.application_args[0] == pad_selector, Int(1)])

        handlers = [
            [Txn.application_id() == Int(0), self.create()],
            [
                Txn.on_completion() == OnComplete.UpdateApplication,
                self.update(),
            ],
            [
                Txn.on_completion() == OnComplete.DeleteApplication,
                self.delete(),
            ],
            *routes,
            [Txn.on_completion() == OnComplete.OptIn, self.optIn()],
            [Txn.on_completion() == OnComplete.CloseOut, self.closeOut()],
            [Txn.on_completion() == OnComplete.ClearState, self.clearState()],
        ]

        return Cond(*handlers)
