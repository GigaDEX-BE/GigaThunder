import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID


class MarketJSON(typing.TypedDict):
    mint: str
    balances: str
    wsol_vault: str
    lot_vault: str
    asks: str
    bids: str


@dataclass
class Market:
    discriminator: typing.ClassVar = b"\xdb\xbe\xd57\x00\xe3\xc6\x9a"
    layout: typing.ClassVar = borsh.CStruct(
        "mint" / BorshPubkey,
        "balances" / BorshPubkey,
        "wsol_vault" / BorshPubkey,
        "lot_vault" / BorshPubkey,
        "asks" / BorshPubkey,
        "bids" / BorshPubkey,
    )
    mint: Pubkey
    balances: Pubkey
    wsol_vault: Pubkey
    lot_vault: Pubkey
    asks: Pubkey
    bids: Pubkey

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Market"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["Market"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Market"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Market":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Market.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            mint=dec.mint,
            balances=dec.balances,
            wsol_vault=dec.wsol_vault,
            lot_vault=dec.lot_vault,
            asks=dec.asks,
            bids=dec.bids,
        )

    def to_json(self) -> MarketJSON:
        return {
            "mint": str(self.mint),
            "balances": str(self.balances),
            "wsol_vault": str(self.wsol_vault),
            "lot_vault": str(self.lot_vault),
            "asks": str(self.asks),
            "bids": str(self.bids),
        }

    @classmethod
    def from_json(cls, obj: MarketJSON) -> "Market":
        return cls(
            mint=Pubkey.from_string(obj["mint"]),
            balances=Pubkey.from_string(obj["balances"]),
            wsol_vault=Pubkey.from_string(obj["wsol_vault"]),
            lot_vault=Pubkey.from_string(obj["lot_vault"]),
            asks=Pubkey.from_string(obj["asks"]),
            bids=Pubkey.from_string(obj["bids"]),
        )
