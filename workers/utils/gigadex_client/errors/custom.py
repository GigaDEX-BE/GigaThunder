import typing
from anchorpy.error import ProgramError


class InvalidTransactionType(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "InvalidTransactionType")

    code = 6000
    name = "InvalidTransactionType"
    msg = "InvalidTransactionType"


class InvalidMetaplexMetadataPda(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "Invalid metaplex metadata pda.")

    code = 6001
    name = "InvalidMetaplexMetadataPda"
    msg = "Invalid metaplex metadata pda."


class VerifiedCreatorAddressMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "Verified creator address mismatch.")

    code = 6002
    name = "VerifiedCreatorAddressMismatch"
    msg = "Verified creator address mismatch."


class InvalidAccountOwner(ProgramError):
    def __init__(self) -> None:
        super().__init__(6003, "Invalid account owner.")

    code = 6003
    name = "InvalidAccountOwner"
    msg = "Invalid account owner."


class InsufficientFeeFunds(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "Insufficient fee funds.")

    code = 6004
    name = "InsufficientFeeFunds"
    msg = "Insufficient fee funds."


class OrderNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6005, "Order Not Found.")

    code = 6005
    name = "OrderNotFound"
    msg = "Order Not Found."


class InvalidAuthPda(ProgramError):
    def __init__(self) -> None:
        super().__init__(6006, "Invalid Authorizer PDA.")

    code = 6006
    name = "InvalidAuthPda"
    msg = "Invalid Authorizer PDA."


class InvalidFeeRxAddress(ProgramError):
    def __init__(self) -> None:
        super().__init__(6007, "Invalid fee receiver address")

    code = 6007
    name = "InvalidFeeRxAddress"
    msg = "Invalid fee receiver address"


class LiquidationCriteriaNotMet(ProgramError):
    def __init__(self) -> None:
        super().__init__(6008, "Liquidation criteria not met")

    code = 6008
    name = "LiquidationCriteriaNotMet"
    msg = "Liquidation criteria not met"


class PriceCrossesSpread(ProgramError):
    def __init__(self) -> None:
        super().__init__(6009, "Price crosses spread.")

    code = 6009
    name = "PriceCrossesSpread"
    msg = "Price crosses spread."


class BalanceTestFailed(ProgramError):
    def __init__(self) -> None:
        super().__init__(6010, "Balance Test Failed.")

    code = 6010
    name = "BalanceTestFailed"
    msg = "Balance Test Failed."


CustomError = typing.Union[
    InvalidTransactionType,
    InvalidMetaplexMetadataPda,
    VerifiedCreatorAddressMismatch,
    InvalidAccountOwner,
    InsufficientFeeFunds,
    OrderNotFound,
    InvalidAuthPda,
    InvalidFeeRxAddress,
    LiquidationCriteriaNotMet,
    PriceCrossesSpread,
    BalanceTestFailed,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: InvalidTransactionType(),
    6001: InvalidMetaplexMetadataPda(),
    6002: VerifiedCreatorAddressMismatch(),
    6003: InvalidAccountOwner(),
    6004: InsufficientFeeFunds(),
    6005: OrderNotFound(),
    6006: InvalidAuthPda(),
    6007: InvalidFeeRxAddress(),
    6008: LiquidationCriteriaNotMet(),
    6009: PriceCrossesSpread(),
    6010: BalanceTestFailed(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
