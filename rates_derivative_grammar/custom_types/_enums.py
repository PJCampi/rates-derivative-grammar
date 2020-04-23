from enum import Enum

__all__ = ['Currency', 'DayCount', 'CapFloorStrategy', 'SettlementMethod', 'SwaptionStrategy']


class Currency(Enum):
    EUR = 1
    USD = 2
    GBP = 3
    CHF = 4
    JPY = 5
    SEK = 6
    DKK = 7
    NOK = 8


class DayCount(Enum):
    ACT360 = 1
    ACT365 = 2
    ACTACT = 3
    BOND = 4


class CapFloorStrategy(Enum):
    CAP = 1
    FLOOR = 2
    STRADDLE = 3
    COLLAR = 4
    STRANGLE = 5


class SettlementMethod(Enum):
    CASH_SETTLED_ISDA = 1
    COLLATERALISED_CASH_PRICE = 2
    PHYSICALLY_SETTLED = 3
    PHYSICALLY_CLEARED_SETTLED = 4
    CASH_SETTLED_PRICED_AS_PHYSICAL = 5


class SwaptionStrategy(Enum):
    PAYER = 1
    RECEIVER = 2
    STRADDLE = 3
    COLLAR = 4
    STRANGLE = 5
