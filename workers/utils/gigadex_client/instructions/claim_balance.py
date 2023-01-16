from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class ClaimBalanceAccounts(typing.TypedDict):
    signer: Pubkey
    user: Pubkey
    market: Pubkey
    balances: Pubkey
    market_auth_pda: Pubkey
    wsol_vault: Pubkey
    lot_vault: Pubkey
    receiver_wsol_ata: Pubkey
    receiver_lot_ata: Pubkey


def claim_balance(
    accounts: ClaimBalanceAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["user"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["balances"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["market_auth_pda"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["wsol_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["lot_vault"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["receiver_wsol_ata"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["receiver_lot_ata"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"Gi\x9b\x1b\xbe\xe8\xe0!"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
