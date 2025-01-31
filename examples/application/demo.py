from algosdk import mnemonic
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    AccountTransactionSigner,
)
from algosdk.v2client.algod import AlgodClient
from algosdk.mnemonic import *

from pytealutils.applications.client import ContractClient
from kitchen_sink import KitchenSink


def print_results(results):
    for result in results.abi_results:
        print("Raw Result: {}".format(result.raw_value))
        print("Parsed Result: {}".format(result.return_value))


# Free money
mnemonic = "movie resource mimic casino kid alpha grass library addict olympic bind when negative slam doll spawn crazy firm material frame reject humble join above crumble"
signer = AccountTransactionSigner(to_private_key(mnemonic))

# Connect to sandbox
client = AlgodClient("a" * 64, "http://localhost:4002")


# Instantiate App Object that is also our pyteal
app = KitchenSink()

# Create app on chain
contract = app.create_app(client, signer)
print("Created {}".format(contract.app_id))

# Create client to make calls with
cc = ContractClient(client, contract, signer)

try:
    print_results(cc.call(cc.reverse, ["desrever yllufsseccus"]))

    print_results(cc.call(cc.concat, [["this", "string", "is", "joined"]]))

    ## Single call, increase budget with dummy calls
    print_results(cc.call(cc.split, ["this string is split"], budget=2))

    # Compose from set of app calls
    comp = AtomicTransactionComposer()
    cc.compose(cc.add, [1, 1], comp)
    cc.compose(cc.sub, [3, 1], comp)
    cc.compose(cc.div, [4, 2], comp)
    cc.compose(cc.mul, [3, 2], comp)
    print_results(comp.execute(cc.client, 2))
except Exception as e:
    print("Fail: {}".format(e))
finally:
    app.delete_app(client, contract.app_id, signer)
    print("Deleted {}".format(contract.app_id))
