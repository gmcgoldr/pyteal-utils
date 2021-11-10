from util.struct import *
from pyteal import *


demo_ints = [50000, 100]
demo_bytes = b"".join([x.to_bytes(8, "big") for x in demo_ints])

data = Bytes(b"deadbeef" * 4 + demo_bytes)


def app():

    definition = [
        ("account", 32, 0),
        ("balance", 8, 1),
        ("rewards", 8, 1),
    ]

    s = Struct(definition)
    gi = s.get_int()
    gb = s.get_bytes()

    return Seq(
        s.store(data),
        Log(gb(Bytes("account"))),
        Log(Itob(gi(Bytes("balance")))),
        Log(Itob(gi(Bytes("rewards")))),
        Int(1),
    )


if __name__ == "__main__":
    print(compileTeal(app(), Mode.Application, version=5))
