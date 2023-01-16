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
from .. import types


class UserBalancesJSON(typing.TypedDict):
    num_users: int
    entries: list[types.entry.EntryJSON]


@dataclass
class UserBalances:
    discriminator: typing.ClassVar = b"\xdf\xe8\xec\t\xd9\xaf\xc6\x84"
    layout: typing.ClassVar = borsh.CStruct(
        "num_users" / borsh.U64, "entries" / types.entry.Entry.layout[10000]
    )
    num_users: int
    entries: list[types.entry.Entry]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["UserBalances"]:
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
    ) -> typing.List[typing.Optional["UserBalances"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["UserBalances"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "UserBalances":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = UserBalances.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            num_users=dec.num_users,
            entries=list(
                map(lambda item: types.entry.Entry.from_decoded(item), dec.entries)
            ),
        )

    def to_json(self) -> UserBalancesJSON:
        return {
            "num_users": self.num_users,
            "entries": list(map(lambda item: item.to_json(), self.entries)),
        }

    @classmethod
    def from_json(cls, obj: UserBalancesJSON) -> "UserBalances":
        return cls(
            num_users=obj["num_users"],
            entries=list(
                map(lambda item: types.entry.Entry.from_json(item), obj["entries"])
            ),
        )
