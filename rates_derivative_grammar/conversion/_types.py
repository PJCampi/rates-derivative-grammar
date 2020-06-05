from bidict import bidict

from ._generic import EnumConverter, DictConverter
from ..custom_types import Currency, DayCount, CapFloorStrategy, SettlementMethod, SwaptionStrategy

__all__ = [
    "CurrencyConverter",
    "DayCountConverter",
    "SwaptionTypeConverter",
    "SwaptionStrategyTypeConverter",
    "CapFLoorTypeConverter",
    "CapFLoorStrategyTypeConverter",
    "SettlementMethodConverter",
]

GRAMMAR = "custom"


class CurrencyConverter(EnumConverter[Currency]):
    grammar = GRAMMAR
    name = "CURRENCY"
    enum = Currency


class DayCountConverter(EnumConverter[DayCount]):
    grammar = GRAMMAR
    name = "DAYCOUNT"
    enum = DayCount


class SwaptionTypeConverter(DictConverter[SwaptionStrategy]):
    grammar = GRAMMAR
    name = "SWAPTION_TYPE"
    mapping = bidict(
        {
            "R": SwaptionStrategy.RECEIVER,
            "P": SwaptionStrategy.PAYER,
            "S": SwaptionStrategy.STRADDLE,
            "WC": SwaptionStrategy.COLLAR,
            "WS": SwaptionStrategy.STRANGLE,
        }
    )


class SwaptionStrategyTypeConverter(SwaptionTypeConverter):
    name = "SWAPTION_STRATEGY_TYPE"


class CapFLoorTypeConverter(DictConverter[CapFloorStrategy]):
    grammar = GRAMMAR
    name = "CAP_FLOOR_TYPE"
    mapping = bidict(
        {
            "C": CapFloorStrategy.CAP,
            "F": CapFloorStrategy.FLOOR,
            "S": CapFloorStrategy.STRADDLE,
            "WC": CapFloorStrategy.COLLAR,
            "WS": CapFloorStrategy.STRANGLE,
        }
    )


class CapFLoorStrategyTypeConverter(CapFLoorTypeConverter):
    name = "CAP_FLOOR_STRATEGY_TYPE"


class SettlementMethodConverter(DictConverter[SettlementMethod]):
    grammar = GRAMMAR
    name = "SETTLEMENT_METHOD"
    mapping = bidict(
        {
            "CASH": SettlementMethod.CASH_SETTLED_ISDA,
            "CCP": SettlementMethod.COLLATERALISED_CASH_PRICE,
            "PHYS": SettlementMethod.PHYSICALLY_SETTLED,
            "PHYSC": SettlementMethod.PHYSICALLY_CLEARED_SETTLED,
            "CASHASPHYS": SettlementMethod.CASH_SETTLED_PRICED_AS_PHYSICAL,
        }
    )
