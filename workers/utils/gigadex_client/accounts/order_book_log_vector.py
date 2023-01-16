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


class OrderBookLogVectorJSON(typing.TypedDict):
    counter: int
    num_logs: int
    order_book_logs: list[types.order_book_log.OrderBookLogJSON]


@dataclass
class OrderBookLogVector:
    discriminator: typing.ClassVar = b"_HD\xbd\xa0\xe9\x05\x17"
    layout: typing.ClassVar = borsh.CStruct(
        "counter" / borsh.U64,
        "num_logs" / borsh.U64,
        "order_book_logs" / types.order_book_log.OrderBookLog.layout[64],
    )
    counter: int
    num_logs: int
    order_book_logs: list[types.order_book_log.OrderBookLog]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["OrderBookLogVector"]:
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
    ) -> typing.List[typing.Optional["OrderBookLogVector"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["OrderBookLogVector"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "OrderBookLogVector":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = OrderBookLogVector.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            counter=dec.counter,
            num_logs=dec.num_logs,
            order_book_logs=list(
                map(
                    lambda item: types.order_book_log.OrderBookLog.from_decoded(item),
                    dec.order_book_logs,
                )
            ),
        )

    def to_json(self) -> OrderBookLogVectorJSON:
        return {
            "counter": self.counter,
            "num_logs": self.num_logs,
            "order_book_logs": list(
                map(lambda item: item.to_json(), self.order_book_logs)
            ),
        }

    @classmethod
    def from_json(cls, obj: OrderBookLogVectorJSON) -> "OrderBookLogVector":
        return cls(
            counter=obj["counter"],
            num_logs=obj["num_logs"],
            order_book_logs=list(
                map(
                    lambda item: types.order_book_log.OrderBookLog.from_json(item),
                    obj["order_book_logs"],
                )
            ),
        )
