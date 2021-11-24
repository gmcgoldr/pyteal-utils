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


def typestring(a):
    typedict = {
        TealType.uint64: "uint64",
        TealType.bytes: "string",
    }
    return typedict[a]


# Utility function to turn a subroutine callable into its selector
def selector(f: Callable) -> str:
    sig = signature(f)
    args = [typestring(p[1].annotation) for p in sig.parameters.items()]
    ret = typestring(f.__closure__[0].cell_contents.returnType)
    method = "{}({}){}".format(f.__name__, ",".join(args), ret)
    return hashy(method)


# Utility function to take the string version of a method signature and
# return the 4 byte selector
def hashy(method: str) -> Bytes:
    chksum = SHA512.new(truncate="256")
    chksum.update(method.encode())
    return Bytes(chksum.digest()[:4])


return_prefix = Bytes("base16", "0x151f7c75")  # Literally hash('return')[:4]


@Subroutine(TealType.none)
def ABIReturn(b: TealType.bytes) -> Expr:
    return Log(Concat(return_prefix, b))


class ABIMethod:
    def __init__(self, ret: tealabi.ABIType):
        self.ret = ret

    def __call__(self, func):
        sig = signature(func)

        args = [v.annotation.__name__.lower() for v in sig.parameters.values()]
        method = "{}({}){}".format(func.__name__, ",".join(args), self.ret.__name__.lower())
        selector = hashy(method)

        # Get the types specified in the method
        abi_codec = [v.annotation for v in sig.parameters.values()]

        # Replace signature with teal native types
        new_params = OrderedDict([
            (k, v.replace(annotation=v.annotation.stack_type))
            for k, v in sig.parameters.items()
        ])
        setattr(func, "signature", method)
        setattr(func, "selector", selector)
        func.__signature__ = sig.replace(parameters=new_params.values())

        # Wrap with encode/decode
        @wraps(func)
        @Subroutine(TealType.uint64)
        def wrapper() -> Expr:
            # Invoke f with decoded arguments
            return Seq(
                ABIReturn(
                self.ret.encode(
                    func(
                        *[
                            abi_codec[idx].decode(Txn.application_args[idx+1])
                            for idx in range(len(abi_codec))
                        ]
                    )
                )
            ),
            Int(1)
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

    # def get_interface(self)->abi.Interface:
    #    abiMethods = []
    #    methods = self.get_methods()
    #    for method in methods:
    #        func = signature(getattr(self, method))

    #    return abi.Interface(self.__class__.__name__, abiMethods)

    def __teal__(self) -> Expr:
        methods = self.get_methods()

        routes = [
            [Txn.application_args[0] == f.selector, f()]
            for f in map(lambda m: getattr(self, m), methods)
        ]

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
