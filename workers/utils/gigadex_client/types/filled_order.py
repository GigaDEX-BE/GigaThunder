from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class FilledOrderJSON(typing.TypedDict):
    price: int
    amount: int
    uid: int


@dataclass
class FilledOrder:
    layout: typing.ClassVar = borsh.CStruct(
        "price" / borsh.U64, "amount" / borsh.U64, "uid" / borsh.U64
    )
    price: int
    amount: int
    uid: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "FilledOrder":
        return cls(price=obj.price, amount=obj.amount, uid=obj.uid)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"price": self.price, "amount": self.amount, "uid": self.uid}

    def to_json(self) -> FilledOrderJSON:
        return {"price": self.price, "amount": self.amount, "uid": self.uid}

    @classmethod
    def from_json(cls, obj: FilledOrderJSON) -> "FilledOrder":
        return cls(price=obj["price"], amount=obj["amount"], uid=obj["uid"])
