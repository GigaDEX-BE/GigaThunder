from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class OrderBookLogJSON(typing.TypedDict):
    key: int
    is_delete: int
    is_insert: int
    is_delta: int
    amount: int
    uid: int
    price: int


@dataclass
class OrderBookLog:
    layout: typing.ClassVar = borsh.CStruct(
        "key" / borsh.U64,
        "is_delete" / borsh.U64,
        "is_insert" / borsh.U64,
        "is_delta" / borsh.U64,
        "amount" / borsh.U64,
        "uid" / borsh.U64,
        "price" / borsh.U64,
    )
    key: int
    is_delete: int
    is_insert: int
    is_delta: int
    amount: int
    uid: int
    price: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "OrderBookLog":
        return cls(
            key=obj.key,
            is_delete=obj.is_delete,
            is_insert=obj.is_insert,
            is_delta=obj.is_delta,
            amount=obj.amount,
            uid=obj.uid,
            price=obj.price,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "key": self.key,
            "is_delete": self.is_delete,
            "is_insert": self.is_insert,
            "is_delta": self.is_delta,
            "amount": self.amount,
            "uid": self.uid,
            "price": self.price,
        }

    def to_json(self) -> OrderBookLogJSON:
        return {
            "key": self.key,
            "is_delete": self.is_delete,
            "is_insert": self.is_insert,
            "is_delta": self.is_delta,
            "amount": self.amount,
            "uid": self.uid,
            "price": self.price,
        }

    @classmethod
    def from_json(cls, obj: OrderBookLogJSON) -> "OrderBookLog":
        return cls(
            key=obj["key"],
            is_delete=obj["is_delete"],
            is_insert=obj["is_insert"],
            is_delta=obj["is_delta"],
            amount=obj["amount"],
            uid=obj["uid"],
            price=obj["price"],
        )
