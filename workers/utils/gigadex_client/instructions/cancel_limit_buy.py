from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class CancelLimitBuyArgs(typing.TypedDict):
    price: int


layout = borsh.CStruct("price" / borsh.U64)


class CancelLimitBuyAccounts(typing.TypedDict):
    signer: Pubkey
    user: Pubkey
    market: Pubkey
    bid_tree: Pubkey
    balances: Pubkey
    bid_logs: Pubkey


def cancel_limit_buy(
    args: CancelLimitBuyArgs,
    accounts: CancelLimitBuyAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["user"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["bid_tree"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["balances"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["bid_logs"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"a\xbd\xben\x13&\x1a\\"
    encoded_args = layout.build(
        {
            "price": args["price"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
