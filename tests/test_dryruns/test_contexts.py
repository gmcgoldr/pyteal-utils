import pytest

from pytealutils.dryruns.contexts import *
from pytealutils.dryruns.contexts import _address_to_idx, _idx_to_address
from pytealutils.dryruns.interop import MAX_SCHEMA


def test_idx_to_address():
    assert (
        _idx_to_address(1)
        == "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVIOOBQA"
    )


def test_address_to_idx():
    assert _address_to_idx(_idx_to_address(1)) == 1


def test_suggested_params_uses_defaults():
    params = AppCallCtx().suggested_params()
    assert params.first == 1
    assert params.last == 1000
    assert params.fee == constants.min_txn_fee
    assert params.flat_fee
    assert not params.gh


def test_suggested_params_uses_round():
    params = AppCallCtx().with_round(123).suggested_params()
    assert params.first == 123
    assert params.last == 1122


def test_with_app_program_uses_defaults():
    ctx = AppCallCtx().with_app_program()
    assert ctx.apps
    assert ctx.apps[0].id == 1
    assert ctx.apps[0].params.global_state_schema == MAX_SCHEMA
    assert ctx.apps[0].params.local_state_schema == MAX_SCHEMA


def test_with_app_program_passes_arguments():
    ctx = AppCallCtx().with_app_program(program=b"code", app_idx=123, state=["state"])
    assert ctx.apps
    assert ctx.apps[0].id == 123
    assert ctx.apps[0].params.approval_program == b"code"
    assert ctx.apps[0].params.global_state == ["state"]


def test_with_account_opted_in_uses_defaults():
    ctx = AppCallCtx().with_app_program().with_app_program().with_account_opted_in()
    assert ctx.accounts
    # starts addresses at 1
    assert ctx.accounts[0].address == _idx_to_address(1)
    # automatically opted into last account
    assert ctx.accounts[0].apps_local_state == [ApplicationLocalState(2)]


def test_with_account_opted_in_passes_arguments():
    ctx = AppCallCtx().with_account_opted_in(123, _idx_to_address(234), ["state"])
    assert ctx.accounts
    assert ctx.accounts[0].address == _idx_to_address(234)
    assert ctx.accounts[0].apps_local_state == [
        ApplicationLocalState(123, key_value=["state"])
    ]


def test_with_txn_call_uses_defaults():
    ctx = AppCallCtx().with_app_program().with_account_opted_in().with_txn_call()
    assert ctx.txns
    assert ctx.txns[0].sender == ctx.accounts[0].address
    assert ctx.txns[0].index == ctx.apps[0].id
    assert ctx.txns[0].on_complete == OnComplete.NoOpOC
    assert ctx.txns[0].accounts == [ctx.accounts[0].address]
    assert ctx.txns[0].foreign_apps == [ctx.apps[0].id]
    assert ctx.txns[0].foreign_assets == None


def test_with_txn_call_passes_arguments():
    ctx = (
        AppCallCtx()
        .with_app_program()
        .with_account_opted_in()
        .with_txn_call(OnComplete.OptInOC, sender=_idx_to_address(123), app_idx=123)
    )
    assert ctx.txns
    assert ctx.txns[0].sender == _idx_to_address(123)
    assert ctx.txns[0].index == 123
    assert ctx.txns[0].on_complete == OnComplete.OptInOC
    assert ctx.txns[0].accounts == [ctx.accounts[0].address]
    assert ctx.txns[0].foreign_apps == [ctx.apps[0].id]
    assert ctx.txns[0].foreign_assets == None
