import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from ..program_id import PROGRAM_ID


class MarketOrderLogJSON(typing.TypedDict):
    amount: int
    total_value_lamports: int
    counter: int


@dataclass
class MarketOrderLog:
    discriminator: typing.ClassVar = b"\x88\x97!\xcfo\x82,\x95"
    layout: typing.ClassVar = borsh.CStruct(
        "amount" / borsh.U64, "total_value_lamports" / borsh.U64, "counter" / borsh.U64
    )
    amount: int
    total_value_lamports: int
    counter: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["MarketOrderLog"]:
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
    ) -> typing.List[typing.Optional["MarketOrderLog"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["MarketOrderLog"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "MarketOrderLog":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = MarketOrderLog.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            amount=dec.amount,
            total_value_lamports=dec.total_value_lamports,
            counter=dec.counter,
        )

    def to_json(self) -> MarketOrderLogJSON:
        return {
            "amount": self.amount,
            "total_value_lamports": self.total_value_lamports,
            "counter": self.counter,
        }

    @classmethod
    def from_json(cls, obj: MarketOrderLogJSON) -> "MarketOrderLog":
        return cls(
            amount=obj["amount"],
            total_value_lamports=obj["total_value_lamports"],
            counter=obj["counter"],
        )
