from abc import ABC, abstractmethod
from typing import Callable
from inspect import signature
from functools import wraps
from Cryptodome.Hash import SHA512
from pyteal import * 

def typestring(a):
    typedict = { TealType.uint64: "uint64", TealType.bytes: "string", }
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

class ABIMethod:
    def __init__(self, ret: TealType):
        self.ret = ret

    def __call__(self, func):
        return Subroutine(self.ret)( func )


class Application(ABC):
    @abstractmethod
    def create(self)->Expr:
        pass

    @abstractmethod
    def update(self)->Expr:
        pass

    @abstractmethod
    def delete(self)->Expr:
        pass

    @abstractmethod
    def optIn(self)->Expr:
        pass

    @abstractmethod
    def closeOut(self)->Expr:
        pass

    @abstractmethod
    def clearState(self)->Expr:
        pass

    def __expr__(self) -> Expr:
        base    = ["clearState", "closeOut", "create", "delete", "optIn", "update"]
        methods = []
        for m in dir(self):
            if m not in base and m[0] != "_" :
                methods.append(m)

        routes = []
        for method in methods:
            func = getattr(self, method)
            # Hardcoded arg passing
            # How do we handle this dynamically?
            routes.append([Txn.application_args[0] == selector(func), func(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))])

        handlers = [
            *routes,
            [Txn.application_id() == Int(0), self.create()],
            [
                Txn.on_completion() == OnComplete.UpdateApplication,
                self.update(),
            ],
            [
                Txn.on_completion() == OnComplete.DeleteApplication,
                self.delete(),
            ],
            [Txn.on_completion() == OnComplete.OptIn, self.optIn()],
            [Txn.on_completion() == OnComplete.CloseOut, self.closeOut()],
            [Txn.on_completion() == OnComplete.ClearState, self.clearState()],
        ]

        return Cond(*handlers)