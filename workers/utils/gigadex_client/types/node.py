from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class NodeJSON(typing.TypedDict):
    price: int
    amount: int
    uid: int
    left: int
    right: int
    next: int
    height: int


@dataclass
class Node:
    layout: typing.ClassVar = borsh.CStruct(
        "price" / borsh.U64,
        "amount" / borsh.U64,
        "uid" / borsh.U64,
        "left" / borsh.U64,
        "right" / borsh.U64,
        "next" / borsh.U64,
        "height" / borsh.U64,
    )
    price: int
    amount: int
    uid: int
    left: int
    right: int
    next: int
    height: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "Node":
        return cls(
            price=obj.price,
            amount=obj.amount,
            uid=obj.uid,
            left=obj.left,
            right=obj.right,
            next=obj.next,
            height=obj.height,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "price": self.price,
            "amount": self.amount,
            "uid": self.uid,
            "left": self.left,
            "right": self.right,
            "next": self.next,
            "height": self.height,
        }

    def to_json(self) -> NodeJSON:
        return {
            "price": self.price,
            "amount": self.amount,
            "uid": self.uid,
            "left": self.left,
            "right": self.right,
            "next": self.next,
            "height": self.height,
        }

    @classmethod
    def from_json(cls, obj: NodeJSON) -> "Node":
        return cls(
            price=obj["price"],
            amount=obj["amount"],
            uid=obj["uid"],
            left=obj["left"],
            right=obj["right"],
            next=obj["next"],
            height=obj["height"],
        )
