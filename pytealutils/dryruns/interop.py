"""Inter-operate with the dryrun API model."""

from base64 import b64decode
from collections import defaultdict
from typing import Dict, List, NamedTuple, Union

from algosdk.v2client.models import (
    Account,
    Application,
    ApplicationLocalState,
    ApplicationParams,
    ApplicationStateSchema,
    TealKeyValue,
    TealValue,
)
from pyteal import *

# TODO: can these values be derived from algosdk constants?
MAX_SCHEMA = ApplicationStateSchema(64, 64)


def _from_value(value: TealValue) -> Union[int, bytes]:
    """Convert a TEAL value to it's Python value."""
    if value is None:
        return None
    if value.get("type", None) == 1:
        value = value.get("bytes", None)
        value = b64decode(value)
    elif value.get("type", None) == 2:
        value = value.get("uint", None)
    return value


class TraceItem(NamedTuple):
    """Information about a call trace line item."""

    # the TEAL source code
    source: str
    # the stack after this line is executed
    stack: List[Union[int, bytes]]
    # the program counter (errors report this value)
    program_counter: int

    def __str__(self) -> str:
        # max 12 char stack value
        stack = [str(v) for v in self.stack]
        stack = [(v[:7] + ".." + v[-3:] if len(v) > 12 else v) for v in stack]
        stack = [f"{v:12s}" for v in stack]
        stack = ", ".join(stack)
        # max 40 char source code
        source = self.source
        if len(source) > 40:
            source = source[:-37] + "..."
        return f"{self.program_counter:5d} :: {source:40s} :: [{stack}]"


class KeyDelta(NamedTuple):
    """Information about a key value which changed."""

    # the key
    key: bytes
    # the new value
    value: int

    @staticmethod
    def from_result(result: Dict) -> "KeyDelta":
        key = b64decode(result["key"])
        value = result["value"].get("uint", None)
        if value is None:
            value = result["value"].get("bytes", None)
            value = b64decode(value)
        return KeyDelta(key, value)


def build_application(
    app_idx: int,
    approval_program: bytes = None,
    clear_state_program: bytes = None,
    global_schema: ApplicationStateSchema = None,
    local_schema: ApplicationStateSchema = None,
    state: List[TealKeyValue] = None,
    creator: str = None,
) -> Application:
    """
    Build an Application with a given `app_idx`.

    With just the `app_idx` specified, the app cannot be used in a transaction.

    The programs can be set to allow the app logic to be called. Note that the
    `approval_program` is the one called for all `on_complete` code other than
    the `ClearState` code. Those transcations will call `clear_state_program`.

    If the schemas are `None`, default to the most permissive schema (64 byte
    slices and 64 ints).

    Use `state` to provide key-value pairs for the app's global state.
    """
    global_schema = global_schema if global_schema is not None else MAX_SCHEMA
    local_schema = local_schema if local_schema is not None else MAX_SCHEMA
    return Application(
        id=app_idx,
        params=ApplicationParams(
            creator=creator,
            global_state=state,
            approval_program=approval_program,
            clear_state_program=clear_state_program,
            global_state_schema=global_schema,
            local_state_schema=local_schema,
        ),
    )


def build_account(
    address: str,
    local_states: List[ApplicationLocalState] = None,
    assets: List[AssetHolding] = None,
    microalgos: int = None,
    status: str = "Offline",
) -> Account:
    """
    Build an account with the given `address`.

    With just the `address` specified, the account cannot be used in a
    transaction.

    Use `local_states` to provide key-value pairs for various apps this account
    has opted into. The actual state can be empty to indicate the account has
    opted in, but has nothing set in its local storage.

    Use `assets` to provide information about assets owned by the account.

    Use `mircoalgos` to provide a balance of Algo owned by the account.
    """
    return Account(
        address=address,
        amount=microalgos,
        apps_local_state=local_states,
        assets=assets,
        status=status,
    )


def check_err(result: Dict):
    """Raise an error if the result contains an execution error."""
    message = result.get("error", None)
    if message:
        raise RuntimeError(f"dryrun error: {message}")


def get_messages(result: Dict, txn_idx: int = 0) -> List[str]:
    """Get the list of execution messages for transaction `txn_idx`."""
    try:
        txn = result.get("txns", [])[txn_idx]
    except IndexError:
        return []
    return txn.get("app-call-messages", [])


def get_trace(result: Dict, txn_idx: int = 0) -> List[TraceItem]:
    """Get the list of trace lines for transaction `txn_idx`."""
    try:
        txn = result.get("txns", [])[txn_idx]
    except IndexError:
        return []

    trace_items = []

    lines = txn.get("disassembly", None)
    trace = txn.get("app-call-trace", None)
    if lines is None or trace is None:
        return []

    for item in trace:
        line = lines[item["line"] - 1]
        stack = [_from_value(i) for i in item["stack"]]
        trace_items.append(TraceItem(line, stack, item["pc"]))

    return trace_items


def get_global_deltas(result: Dict, txn_idx: int = 0) -> List[KeyDelta]:
    """Get the list of global key deltas for transaction `txn_idx`."""
    try:
        txn = result.get("txns", [])[txn_idx]
    except IndexError:
        return []
    return [KeyDelta.from_result(d) for d in txn.get("global-delta")]


def get_local_deltas(result: Dict, txn_idx: int = 0) -> Dict[str, List[KeyDelta]]:
    """Get the list of local key deltas for transaction `txn_idx`."""
    try:
        txn = result.get("txns", [])[txn_idx]
    except IndexError:
        return []

    local_deltas = defaultdict(list)
    for local_delta in txn.get("local-deltas", []):
        address = local_delta["address"]
        deltas = local_delta["delta"]
        if address is None or deltas is None:
            continue
        local_deltas[address] += [KeyDelta.from_result(d) for d in deltas]

    return dict(local_deltas)
