import base64
from typing import List
from algosdk.v2client import algod
from algosdk.abi import Method, Contract
from algosdk.v2client.algod import AlgodClient
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
    TransactionSigner,
)
from algosdk.future.transaction import (
    ApplicationCreateTxn,
    ApplicationNoOpTxn,
    OnComplete,
    wait_for_confirmation,
)
from algosdk.account import address_from_private_key
from application import Application

# TODO: signer should return address
# TODO: create contract from interface and id


class ContractClient:
    def __init__(self, app: Application, signer: TransactionSigner = None):
        self.client = AlgodClient("a" * 64, "http://localhost:4002")

        self.app = app
        self.contract = app.get_contract(0)
        self.signer = signer

        self.addr = address_from_private_key(self.signer.private_key)
        self.app_id = 0  # app.app_id

        for m in self.contract.methods:
            setattr(self, m.name, m)

    def deploy(self) -> int:
        sp = self.client.suggested_params()

        approval_result = self.client.compile(self.app.approval_source())
        approval_program = base64.b64decode(approval_result["result"])

        clear_result = self.client.compile(self.app.clear_source())
        clear_program = base64.b64decode(clear_result["result"])

        ctx = AtomicTransactionComposer()
        ctx.add_transaction(
            TransactionWithSigner(
                ApplicationCreateTxn(
                    self.addr,
                    sp,
                    OnComplete.NoOpOC,
                    approval_program,
                    clear_program,
                    self.app.global_schema(),
                    self.app.local_schema(),
                ),
                self.signer,
            )
        )
        txids = ctx.submit(self.client)
        result = wait_for_confirmation(self.client, txids[0])
        self.app_id = result["application-index"]
        return self.app_id

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
