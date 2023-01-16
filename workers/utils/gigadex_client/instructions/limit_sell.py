from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class LimitSellArgs(typing.TypedDict):
    price: int
    amount: int


layout = borsh.CStruct("price" / borsh.U64, "amount" / borsh.U64)


class LimitSellAccounts(typing.TypedDict):
    signer: Pubkey
    user: Pubkey
    market: Pubkey
    ask_tree: Pubkey
    bid_tree: Pubkey
    lot_vault: Pubkey
    sender_lot_ata: Pubkey
    ask_logs: Pubkey


def limit_sell(
    args: LimitSellArgs,
    accounts: LimitSellAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["user"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["ask_tree"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["bid_tree"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["lot_vault"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["sender_lot_ata"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["ask_logs"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"n\x84\xbd\xd1\xc8@7["
    encoded_args = layout.build(
        {
            "price": args["price"],
            "amount": args["amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
