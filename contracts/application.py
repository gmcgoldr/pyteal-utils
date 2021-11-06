from abc import ABC, abstractmethod
from pyteal import Txn, Return, Int, Expr, OnComplete, Cond, compileTeal, Mode, TealType

class Application(ABC):

    def Method(func):
        def abi(*args, **kwargs):
            print(args, kwargs)
            func(*args, **kwargs)
        return abi 

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def optIn(self):
        pass

    @abstractmethod
    def closeOut(self):
        pass

    @abstractmethod
    def clearState(self):
        pass

    def __expr__(self) -> Expr:
        handlers = [
            [Txn.application_id() == Int(0),                        Return(self.create())],
            [Txn.on_completion()  == OnComplete.UpdateApplication,  Return(self.update())],
            [Txn.on_completion()  == OnComplete.DeleteApplication,  Return(self.delete())],
            [Txn.on_completion()  == OnComplete.OptIn,              Return(self.optIn())],
            [Txn.on_completion()  == OnComplete.CloseOut,           Return(self.closeOut())],
            [Txn.on_completion()  == OnComplete.ClearState,         Return(self.clearState())],
        ]

        print(self.add.__func__.__name__)
        #for x in self.__class__:
        #    print(dir(x))

        return Cond(*handlers)






class MyApp(Application):

    def create(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def optIn(self):
        pass

    def closeOut(self):
        pass

    def clearState(self):
        pass

    @Application.Method
    def add(self, a: TealType.uint64, b: TealType.uint64):
        return a + b

    @Application.Method
    def subtract(self, a: TealType.uint64, b: TealType.uint64):
        return a - b


m = MyApp()
expr = m.__expr__()
