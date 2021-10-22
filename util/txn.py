from pyteal import Global, TealType, Subroutine, Assert

@Subroutine(TealType.none)
def no_rekey(txn):
    return Assert(txn.rekey_to() == Global.zero_address)

@Subroutine(TealType.none)
def no_close_to(txn):
    return Assert(txn.close_remaineder_to() == Global.zero_address)

@Subroutine(TealType.none)
def no_asset_close_to(txn):
    return Assert(txn.asset_close_to() == Global.zero_address)

