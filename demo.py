from pyteal import * 
from util.struct import * 


demo_ints  = [50000, 100]
demo_bytes = b"".join([x.to_bytes(8,'big') for x in demo_ints])

data = Bytes(b"deadbeef"+demo_bytes)


def app():

    definition = [
        (Bytes("account"), 8, 0),
        (Bytes("balance"), 8, 1),
        (Bytes("rewards"), 8, 1),
    ]

    s = Struct(definition)
    gi = s.get_int()
    gb = s.get_bytes()

    return Seq(
        s.store(data),
        Log(gb(Bytes("account"))),
        Log(Itob(gi(Bytes("balance")))),
        Log(Itob(gi(Bytes("rewards")))),
        Int(1)
    )


if __name__ == "__main__":
    print(compileTeal(app(), Mode.Application, version=5))
