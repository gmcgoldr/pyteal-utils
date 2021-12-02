
from pyteal import * 

from pytealutils.abi import String
from pytealutils.applications import ABIMethod
from pytealutils.applications.defaults import DefaultApprove 

class Example(DefaultApprove):

    @staticmethod
    @ABIMethod
    def echo(a: String)->String:
        return a


if __name__ == "__main__":
    import json
    app = Example()

    with open("interface.json", "w") as f:
        f.write(json.dumps(app.get_interface().dictify()))

    with open("approval.teal", "w") as f:
        f.write(
            compileTeal(
                app.handler(), mode=Mode.Application, version=5, assembleConstants=True
            )
        )