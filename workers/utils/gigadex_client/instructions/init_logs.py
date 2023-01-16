from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class InitLogsAccounts(typing.TypedDict):
    signer: Pubkey
    market: Pubkey
    buy_order_log: Pubkey
    sell_order_log: Pubkey
    bid_logs: Pubkey
    ask_logs: Pubkey


def init_logs(
    accounts: InitLogsAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["buy_order_log"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["sell_order_log"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["bid_logs"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["ask_logs"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\t\xd7\xa8z\x82f\x8e\x01"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
