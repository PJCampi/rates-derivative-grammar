from ._base import Processor, processors_registry
from ._generic import SingleSizeProcessorMixin, RelativeStrikeProcessorMixin


__all__ = ["CapFloorProcessor", "CapFloorStrategyProcessor", "SwaptionProcessor", "SwaptionStrategyProcessor"]


class RatesVolatilityProcessor(Processor):
    grammar = "rates_volatility"


class CapFloorProcessor(SingleSizeProcessorMixin, RelativeStrikeProcessorMixin, RatesVolatilityProcessor):
    product_type = "cap_floor"
    attribute_names = (
        "currency",
        "start_time",
        "end_time",
        "is_relative",
        "strike",
        "contract_type",
        "float_freq",
        "size",
    )


class CapFloorStrategyProcessor(SingleSizeProcessorMixin, RelativeStrikeProcessorMixin, RatesVolatilityProcessor):
    product_type = "cap_floor_strategy"
    attribute_names = (
        "currency",
        "start_time",
        "end_time",
        "is_relative",
        "strike",
        "width",
        "contract_type",
        "float_freq",
        "size",
    )


class SwaptionProcessor(SingleSizeProcessorMixin, RelativeStrikeProcessorMixin, RatesVolatilityProcessor):
    product_type = "swaption"
    attribute_names = (
        "currency",
        "start_time",
        "end_time",
        "is_relative",
        "strike",
        "contract_type",
        "float_freq",
        "settlement_method",
        "size",
    )


class SwaptionStrategyProcessor(SingleSizeProcessorMixin, RelativeStrikeProcessorMixin, RatesVolatilityProcessor):
    product_type = "swaption_strategy"
    attribute_names = (
        "currency",
        "start_time",
        "end_time",
        "is_relative",
        "strike",
        "width",
        "contract_type",
        "float_freq",
        "settlement_method",
        "size",
    )


processors_registry[CapFloorProcessor.to_key()] = CapFloorProcessor
processors_registry[CapFloorStrategyProcessor.to_key()] = CapFloorStrategyProcessor
processors_registry[SwaptionProcessor.to_key()] = SwaptionProcessor
processors_registry[SwaptionStrategyProcessor.to_key()] = SwaptionStrategyProcessor
