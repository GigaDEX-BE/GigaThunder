from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class LimitBuyArgs(typing.TypedDict):
    price: int
    amount: int


layout = borsh.CStruct("price" / borsh.U64, "amount" / borsh.U64)


class LimitBuyAccounts(typing.TypedDict):
    signer: Pubkey
    user: Pubkey
    market: Pubkey
    bid_tree: Pubkey
    ask_tree: Pubkey
    wsol_vault: Pubkey
    bid_logs: Pubkey


def limit_buy(
    args: LimitBuyArgs,
    accounts: LimitBuyAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["user"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["bid_tree"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["ask_tree"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["wsol_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["bid_logs"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x82\xd7\xdai\xc4\x0e\xe3D"
    encoded_args = layout.build(
        {
            "price": args["price"],
            "amount": args["amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
