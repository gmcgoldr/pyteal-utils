from algosdk import mnemonic
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    AccountTransactionSigner,
)
from algosdk.v2client.algod import AlgodClient
from algosdk.mnemonic import *

from client import ContractClient
from kitchen_sink import KitchenSink

mnemonic = "movie resource mimic casino kid alpha grass library addict olympic bind when negative slam doll spawn crazy firm material frame reject humble join above crumble"
sk = to_private_key(mnemonic)
signer = AccountTransactionSigner(sk)

client = AlgodClient("a" * 64, "http://localhost:4002")

app = KitchenSink()

app_id = 306
# Deploy
# contract = app.deploy_app(client, signer)
# app_id=contract.app_id
# print("Created {}".format(contract.app_id))

# update
contract = app.update_app(app_id, client, signer)
print("Updated {}".format(contract.app_id))


# Create client to make calls with
cc = ContractClient(client, contract, signer)

# Single call, increase budget with "pad" method
result = cc.call(cc.reverse, ["desrever yllufsseccus"])
print("Result of single call: {}".format(result.abi_results[0].return_value))

# Compose from set of
comp = AtomicTransactionComposer()
cc.compose(comp, cc.add, [1, 1])
cc.compose(comp, cc.sub, [3, 1])
cc.compose(comp, cc.div, [4, 2])
cc.compose(comp, cc.mul, [3, 2])
result = comp.execute(cc.client, 2)
print("Result of group: {}".format([r.return_value for r in result.abi_results]))
