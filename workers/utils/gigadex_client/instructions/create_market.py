from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class CreateMarketAccounts(typing.TypedDict):
    signer: Pubkey
    bid_tree: Pubkey
    ask_tree: Pubkey
    balances: Pubkey
    wsol_mint: Pubkey
    lot_mint: Pubkey
    market: Pubkey
    market_auth_pda: Pubkey
    wsol_vault: Pubkey
    lot_vault: Pubkey


def create_market(
    accounts: CreateMarketAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["bid_tree"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["ask_tree"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["balances"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["wsol_mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["lot_mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["market"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["market_auth_pda"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["wsol_vault"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["lot_vault"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"g\xe2a\xeb\xc8\xbc\xfb\xfe"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
