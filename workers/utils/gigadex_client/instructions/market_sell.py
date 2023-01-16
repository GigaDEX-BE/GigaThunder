from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class MarketSellArgs(typing.TypedDict):
    amount: int


layout = borsh.CStruct("amount" / borsh.U64)


class MarketSellAccounts(typing.TypedDict):
    signer: Pubkey
    user: Pubkey
    market: Pubkey
    balances: Pubkey
    bid_tree: Pubkey
    sender_lot_ata: Pubkey
    lot_vault: Pubkey
    fee_receiver_address: Pubkey
    sell_order_log: Pubkey
    bid_logs: Pubkey


def market_sell(
    args: MarketSellArgs,
    accounts: MarketSellAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["user"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["balances"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["bid_tree"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["sender_lot_ata"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["lot_vault"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["fee_receiver_address"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["sell_order_log"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["bid_logs"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x0b\xe0\x9fw\x81\x7f\x91\xed"
    encoded_args = layout.build(
        {
            "amount": args["amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
