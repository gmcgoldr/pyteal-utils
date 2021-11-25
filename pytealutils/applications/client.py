from typing import List
from algosdk.v2client import algod
from algosdk.abi import Method, Contract
from algosdk.v2client.algod import AlgodClient
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionSigner,
)
from algosdk.account import address_from_private_key

# TODO: signer should return address
# TODO: create contract from interface and id


class ContractClient:
    def __init__(self, contract: Contract, signer: TransactionSigner = None):
        self.client = AlgodClient("a" * 64, "http://localhost:4002")
        self.contract = contract
        self.signer = signer

        self.addr = address_from_private_key(self.signer.private_key)
        self.app_id = contract.app_id

        for m in contract.methods:
            setattr(self, m.name, m)

    def compose(self, ctx: AtomicTransactionComposer, method: Method, args: List[any]):
        # TODO: cacheme
        sp = self.client.suggested_params()
        ctx.add_method_call(
            self.app_id, method, self.addr, sp, self.signer, method_args=args
        )

    def call(self, method: Method, args: List[any], budget=1):
        ctx = AtomicTransactionComposer()

        sp = self.client.suggested_params()
        ctx.add_method_call(
            self.app_id, method, self.addr, sp, self.signer, method_args=args
        )

        for _ in range(budget - 1):
            ctx.add_method_call(self.app_id, self.pad, self.addr, sp, self.signer)

        return ctx.execute(self.client, 2)
