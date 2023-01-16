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
from .. import types


class OrderTreeJSON(typing.TypedDict):
    root_idx: int
    market_buy: int
    nodes: list[types.node.NodeJSON]
    num_orders: int
    current_signer: str
    remaining_amount: int
    num_fills: int
    fills: list[types.filled_order.FilledOrderJSON]
    num_deltas: int
    node_delta: list[types.node_delta_log.NodeDeltaLogJSON]
    amount_cancelled: int


@dataclass
class OrderTree:
    discriminator: typing.ClassVar = b"i\xe8\xad\x91\xa8'\xc7o"
    layout: typing.ClassVar = borsh.CStruct(
        "root_idx" / borsh.U64,
        "market_buy" / borsh.U64,
        "nodes" / types.node.Node.layout[10000],
        "num_orders" / borsh.U64,
        "current_signer" / BorshPubkey,
        "remaining_amount" / borsh.U64,
        "num_fills" / borsh.U64,
        "fills" / types.filled_order.FilledOrder.layout[64],
        "num_deltas" / borsh.U64,
        "node_delta" / types.node_delta_log.NodeDeltaLog.layout[64],
        "amount_cancelled" / borsh.U64,
    )
    root_idx: int
    market_buy: int
    nodes: list[types.node.Node]
    num_orders: int
    current_signer: Pubkey
    remaining_amount: int
    num_fills: int
    fills: list[types.filled_order.FilledOrder]
    num_deltas: int
    node_delta: list[types.node_delta_log.NodeDeltaLog]
    amount_cancelled: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["OrderTree"]:
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
    ) -> typing.List[typing.Optional["OrderTree"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["OrderTree"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "OrderTree":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = OrderTree.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            root_idx=dec.root_idx,
            market_buy=dec.market_buy,
            nodes=list(map(lambda item: types.node.Node.from_decoded(item), dec.nodes)),
            num_orders=dec.num_orders,
            current_signer=dec.current_signer,
            remaining_amount=dec.remaining_amount,
            num_fills=dec.num_fills,
            fills=list(
                map(
                    lambda item: types.filled_order.FilledOrder.from_decoded(item),
                    dec.fills,
                )
            ),
            num_deltas=dec.num_deltas,
            node_delta=list(
                map(
                    lambda item: types.node_delta_log.NodeDeltaLog.from_decoded(item),
                    dec.node_delta,
                )
            ),
            amount_cancelled=dec.amount_cancelled,
        )

    def to_json(self) -> OrderTreeJSON:
        return {
            "root_idx": self.root_idx,
            "market_buy": self.market_buy,
            "nodes": list(map(lambda item: item.to_json(), self.nodes)),
            "num_orders": self.num_orders,
            "current_signer": str(self.current_signer),
            "remaining_amount": self.remaining_amount,
            "num_fills": self.num_fills,
            "fills": list(map(lambda item: item.to_json(), self.fills)),
            "num_deltas": self.num_deltas,
            "node_delta": list(map(lambda item: item.to_json(), self.node_delta)),
            "amount_cancelled": self.amount_cancelled,
        }

    @classmethod
    def from_json(cls, obj: OrderTreeJSON) -> "OrderTree":
        return cls(
            root_idx=obj["root_idx"],
            market_buy=obj["market_buy"],
            nodes=list(map(lambda item: types.node.Node.from_json(item), obj["nodes"])),
            num_orders=obj["num_orders"],
            current_signer=Pubkey.from_string(obj["current_signer"]),
            remaining_amount=obj["remaining_amount"],
            num_fills=obj["num_fills"],
            fills=list(
                map(
                    lambda item: types.filled_order.FilledOrder.from_json(item),
                    obj["fills"],
                )
            ),
            num_deltas=obj["num_deltas"],
            node_delta=list(
                map(
                    lambda item: types.node_delta_log.NodeDeltaLog.from_json(item),
                    obj["node_delta"],
                )
            ),
            amount_cancelled=obj["amount_cancelled"],
        )
