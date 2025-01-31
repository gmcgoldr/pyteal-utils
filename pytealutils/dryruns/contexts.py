"""Context objects used to encapsulate dryrun state."""

from copy import deepcopy
from typing import List

from algosdk import constants
from algosdk.encoding import decode_address, encode_address
from algosdk.future.transaction import (
    ApplicationCallTxn,
    OnComplete,
    SignedTransaction,
    SuggestedParams,
    Transaction,
)
from algosdk.testing.dryrun import ZERO_ADDRESS, DryrunRequest
from algosdk.v2client.models import (
    Account,
    Application,
    ApplicationLocalState,
    Asset,
    TealKeyValue,
)

from .interop import build_account, build_application


def _idx_to_address(idx: int) -> str:
    """Build an address whose integer value is `idx`."""
    return encode_address(idx.to_bytes(constants.key_len_bytes, "big"))


def _address_to_idx(address: str) -> int:
    """Calculate the integer value of a key, modulo `2**64`."""
    return int.from_bytes(decode_address(address)[-8:], "big")


class AppCallCtx:
    """
    Build up the full context (arguments) which are accessible by app calls
    generated by a group of transactions (or a single transaction).

    NOTE: the `with_` methods are not commutative. For example, calling
    `with_account_opted_in` after `with_app` will opt-in the new account to the
    last app id.
    """

    def __init__(self):
        # applications with state and / or logic accessed by transactions
        self.apps: List[Application] = []
        # transactions, at least one of which should call an app
        self.txns: List[Transaction] = []
        # accounts state accessed by the apps
        self.accounts: List[Account] = []
        # assets accessed by the apps
        self.assets: List[Asset] = []
        # last timestamp on the ledger
        self.latest_timestamp: int = None
        # last round number on the ledger
        self.round: int = None

    def _next_app_idx(self) -> int:
        if not self.apps:
            return 1
        app_idxs = {a.id for a in self.apps}
        for idx in sorted(app_idxs):
            if idx < 2 ** 64 - 1 and idx + 1 not in app_idxs:
                return idx + 1
        # system will be out of memory before this happens
        return None

    def _next_account_address(self) -> str:
        if not self.accounts:
            return _idx_to_address(1)
        account_idxs = {_address_to_idx(a.address) for a in self.accounts}
        for idx in sorted(account_idxs):
            if idx < 2 ** 64 - 1 and idx + 1 not in account_idxs:
                return _idx_to_address(idx + 1)
        # system will be out of memory before this happens
        return None

    def _last_app_idx(self) -> int:
        return self.apps[-1].id if self.apps else 0

    def _last_account_address(self) -> str:
        return self.accounts[-1].address if self.accounts else ZERO_ADDRESS

    def suggested_params(self) -> SuggestedParams:
        """
        Build minimal transaction parameters which will work with dry run.

        Defaults to using the minimal network fee, and allowing the maximum
        transaction lifetime for execution, from the current `round` or from
        the first round.
        """
        first = self.round if self.round is not None else 1
        return SuggestedParams(
            fee=constants.min_txn_fee,
            first=first,
            # currently this is the network's maximum transaction life, but this
            # could change and isn't part of the SDK
            last=first + 1000 - 1,
            gh="",
            flat_fee=True,
        )

    def with_latest_timestamp(self, latest_timestamp: int) -> "AppCallCtx":
        """Set the latest timestamp (`Global.latest_timestamp`)"""
        ctx = deepcopy(self)
        ctx.latest_timestamp = latest_timestamp
        return ctx

    def with_round(self, round: int) -> "AppCallCtx":
        """Set the last round (`Global.round`)"""
        ctx = deepcopy(self)
        ctx.round = round
        return ctx

    def with_app(self, app: Application) -> "AppCallCtx":
        """
        Add an application. If this application is being called, its source
        program(s) must be supplied.
        """
        ctx = deepcopy(self)
        ctx.apps.append(deepcopy(app))
        return ctx

    def with_app_program(
        self,
        program: bytes = None,
        app_idx: int = None,
        state: List[TealKeyValue] = None,
    ) -> "AppCallCtx":
        """
        Add an application with defaults and possibly an approval program.

        If `app_idx` is omitted, defaults to the next available app idx not in
        the `apps`.
        """
        app_idx = app_idx if app_idx is not None else self._next_app_idx()
        return self.with_app(
            build_application(app_idx=app_idx, approval_program=program, state=state)
        )

    def with_account(self, account: Account) -> "AppCallCtx":
        """Add an account with some local state."""
        ctx = deepcopy(self)
        ctx.accounts.append(deepcopy(account))
        return ctx

    def with_account_opted_in(
        self,
        app_idx: int = None,
        address: str = None,
        local_state: List[TealKeyValue] = None,
    ) -> "AppCallCtx":
        """
        Add an account which is opted into to an app.

        If `app_idx` is omitted, defaults to the index of the last added app.

        If `address` is omitted, defaults to the next available address not in
        the `accounts`.

        If `local_state` isn't provided, then the account is seen to be opted
        into the app, but with no local storage set.
        """
        address = address if address is not None else self._next_account_address()
        app_idx = app_idx if app_idx is not None else self._last_app_idx()
        account = build_account(
            address,
            local_states=[ApplicationLocalState(id=app_idx, key_value=local_state)],
        )
        return self.with_account(account)

    def with_txn(self, txn: Transaction) -> "AppCallCtx":
        """
        Add a transaction.

        NOTE: for an `ApplicationCreateTxn`, the transaction sender must match
        the application creator. The zero address can be used for both.
        """
        ctx = deepcopy(self)
        ctx.txns.append(deepcopy(txn))
        return ctx

    def with_txn_call(
        self,
        on_complete: OnComplete = OnComplete.NoOpOC,
        sender: str = None,
        params: SuggestedParams = None,
        app_idx: int = None,
        args: List[bytes] = None,
    ) -> "AppCallCtx":
        """
        Add a transaction which calls an app.

        If `sender` is omitted, defaults to the address of the last added
        account.

        If `params` is omitted, defaults to the result of `suggested_params`.

        If `app_idx` is omitted, defaults to the index of the last added app.
        """
        app_idx = app_idx if app_idx is not None else self._last_app_idx()
        return self.with_txn(
            ApplicationCallTxn(
                sender=sender if sender is not None else self._last_account_address(),
                sp=params if params is not None else self.suggested_params(),
                index=app_idx,
                on_complete=on_complete,
                app_args=args,
                accounts=[a.address for a in self.accounts],
                foreign_apps=[a.id for a in self.apps],
                foreign_assets=[a.index for a in self.assets],
            )
        )

    def build_request(self) -> DryrunRequest:
        """Build the dry run request."""
        # dryrun expects signed transactions but doesn't actually use the
        # signature data, so set it to None
        signed_txns = [
            SignedTransaction(t, None) if not isinstance(t, SignedTransaction) else t
            for t in self.txns
        ]
        return DryrunRequest(
            txns=signed_txns,
            apps=self.apps,
            accounts=self.accounts,
            # not clear if this is accessed anywhere
            protocol_version=None,
            round=self.round,
            latest_timestamp=self.latest_timestamp,
            # sources are already compiled and included in the apps
            sources=None,
        )
