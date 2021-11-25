from algosdk import mnemonic, abi
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    AccountTransactionSigner,
)
from algosdk.mnemonic import *

from client import ContractClient
from kitchen_sink import KitchenSink

mnemonic = "hobby other dilemma add wool nurse insane cinnamon doctor swarm fan same usage sock mirror clever mention situate reason subject curtain tired flat able hunt"
sk = to_private_key(mnemonic)
addr = to_public_key(mnemonic)

app = KitchenSink()

cc = ContractClient(app.get_contract(139), AccountTransactionSigner(sk))

# Single call, increase budget with "pad" method
result = cc.call(cc.reverse, ["desrever yllufsseccus"], budget=2)
print(result.abi_results[0].return_value)

# Compose from set of
comp = AtomicTransactionComposer()
cc.compose(comp, cc.add, [1, 1])
cc.compose(comp, cc.sub, [3, 1])
cc.compose(comp, cc.div, [4, 2])
cc.compose(comp, cc.mul, [3, 2])
resp = comp.execute(cc.client, 2)
print([r.return_value for r in resp.abi_results])
