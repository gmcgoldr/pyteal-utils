from algosdk import mnemonic, abi
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    AccountTransactionSigner,
)
from algosdk.mnemonic import *

from client import ContractClient
from kitchen_sink import KitchenSink

mnemonic = "movie resource mimic casino kid alpha grass library addict olympic bind when negative slam doll spawn crazy firm material frame reject humble join above crumble"
sk = to_private_key(mnemonic)
addr = to_public_key(mnemonic)

app = KitchenSink()

cc = ContractClient(app, AccountTransactionSigner(sk))

# Deploy and set new app id on contract client
app_id = cc.deploy()
print("Created {}".format(app_id))

# Single call, increase budget with "pad" method
result = cc.call(cc.reverse, ["desrever yllufsseccus"], budget=2)
print("Result of single call: {}".format(result.abi_results[0].return_value))

# Compose from set of
comp = AtomicTransactionComposer()
cc.compose(comp, cc.add, [1, 1])
cc.compose(comp, cc.sub, [3, 1])
cc.compose(comp, cc.div, [4, 2])
cc.compose(comp, cc.mul, [3, 2])
result = comp.execute(cc.client, 2)
print("Result of group: {}".format([r.return_value for r in result.abi_results]))
