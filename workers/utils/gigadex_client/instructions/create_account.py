from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class CreateAccountAccounts(typing.TypedDict):
    signer: Pubkey
    market: Pubkey
    balances: Pubkey
    user: Pubkey


def create_account(
    accounts: CreateAccountAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["balances"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["user"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"c\x14\x82w\xc4\xeb\x83\x95"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
