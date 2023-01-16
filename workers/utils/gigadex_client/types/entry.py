from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class EntryJSON(typing.TypedDict):
    lamports: int
    lots: int


@dataclass
class Entry:
    layout: typing.ClassVar = borsh.CStruct("lamports" / borsh.U64, "lots" / borsh.U64)
    lamports: int
    lots: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "Entry":
        return cls(lamports=obj.lamports, lots=obj.lots)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"lamports": self.lamports, "lots": self.lots}

    def to_json(self) -> EntryJSON:
        return {"lamports": self.lamports, "lots": self.lots}

    @classmethod
    def from_json(cls, obj: EntryJSON) -> "Entry":
        return cls(lamports=obj["lamports"], lots=obj["lots"])
