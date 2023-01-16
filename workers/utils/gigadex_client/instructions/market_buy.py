from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class MarketBuyArgs(typing.TypedDict):
    amount: int


layout = borsh.CStruct("amount" / borsh.U64)


class MarketBuyAccounts(typing.TypedDict):
    signer: Pubkey
    user: Pubkey
    market: Pubkey
    balances: Pubkey
    ask_tree: Pubkey
    wsol_vault: Pubkey
    fee_receiver_address: Pubkey
    buy_order_log: Pubkey
    ask_logs: Pubkey


def market_buy(
    args: MarketBuyArgs,
    accounts: MarketBuyAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["user"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["balances"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["ask_tree"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["wsol_vault"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["fee_receiver_address"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["buy_order_log"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["ask_logs"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"Z\xecj\xdc\xddQl\x8c"
    encoded_args = layout.build(
        {
            "amount": args["amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
