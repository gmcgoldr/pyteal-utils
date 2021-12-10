import pytest

from pytealutils.dryruns.interop import *
from pytealutils.dryruns.interop import _from_value


def test_from_value_decodes_values():
    assert _from_value({"type": 1, "bytes": "YQ==", "uint": None}) == b"a"
    assert _from_value({"type": 2, "bytes": b"", "uint": 1}) == 1


def test_build_application_uses_defaults():
    app = build_application(1)
    assert app.id == 1
    assert app.params.creator is None
    assert app.params.approval_program is None
    assert app.params.clear_state_program is None
    assert app.params.global_state_schema == MAX_SCHEMA
    assert app.params.local_state_schema == MAX_SCHEMA


def test_build_application_passes_arguments():
    app = build_application(
        1,
        b"approval",
        b"clear",
        ApplicationStateSchema(1, 2),
        ApplicationStateSchema(2, 3),
        ["state"],
        b"creator",
    )
    assert app.id == 1
    assert app.params.creator == b"creator"
    assert app.params.approval_program == b"approval"
    assert app.params.clear_state_program == b"clear"
    assert app.params.global_state_schema == ApplicationStateSchema(1, 2)
    assert app.params.local_state_schema == ApplicationStateSchema(2, 3)


def test_build_account_uses_defaults():
    account = build_account("address")
    assert account.address == "address"
    assert account.amount is None
    assert account.apps_local_state is None
    assert account.assets is None
    assert account.status == "Offline"


def test_build_account_passes_arguments():
    account = build_account("address", ["state"], ["asset"], 123, "status")
    assert account.address == "address"
    assert account.amount == 123
    assert account.apps_local_state == ["state"]
    assert account.assets == ["asset"]
    assert account.status == "status"


def test_check_err_raises_error():
    result = {"error": "message"}
    with pytest.raises(RuntimeError, match="message"):
        check_err(result)


def test_get_messages_returns_message_for_transaction():
    result = {"txns": [None, {"app-call-messages": ["a", "b"]}]}
    assert get_messages(result, 1) == ["a", "b"]
