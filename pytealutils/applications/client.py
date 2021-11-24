from pyteal import *
from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk.v2client.algod import *
from algosdk.atomic_transaction_composer import *
from algosdk.future.transaction import *
from algosdk.abi import *
from algosdk.mnemonic import *
from algosdk.account import *


from sys import path
from os.path import dirname, abspath

path.append(dirname(abspath(__file__)) + "/..")
import abi

from kitchen_sink import KitchenSink

client = algod.AlgodClient("a" * 64, "http://localhost:4002")

app = KitchenSink()

interface = app.get_interface()


def get_method(name: str) -> Method:
    for m in interface.methods:
        if m.name == name:
            return m
    raise Exception("No method with that name")


mnemonic = "hobby other dilemma add wool nurse insane cinnamon doctor swarm fan same usage sock mirror clever mention situate reason subject curtain tired flat able hunt"

sk = to_private_key(mnemonic)
addr = to_public_key(mnemonic)


app_id = 139

sp = client.suggested_params()

signer = AccountTransactionSigner(sk)

comp = AtomicTransactionComposer()
comp.add_method_call(app_id, get_method("add"), addr, sp, signer, method_args=[1, 1])
comp.add_method_call(app_id, get_method("sub"), addr, sp, signer, method_args=[3, 1])
comp.add_method_call(app_id, get_method("div"), addr, sp, signer, method_args=[4, 2])
comp.add_method_call(app_id, get_method("mul"), addr, sp, signer, method_args=[3, 2])
comp.add_method_call(
    app_id,
    get_method("reverse"),
    addr,
    sp,
    signer,
    method_args=["desrever yllufsseccus"],
)

resp = comp.execute(client, 2)

for result in resp.abi_results:
    print(result.return_value)
