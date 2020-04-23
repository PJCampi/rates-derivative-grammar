
from ._base import Processor, processors_registry
from ._generic import SingleSizeProcessorMixin, MultiSizeProcessorMixin, LeverageScheduleProcessorMixin


__all__ = ['CrossCurrencySwapProcessor', 'FixFloatSwapProcessor', 'FraProcessor', 'TenorBasisSwapProcessor',
           'SwapCurveProcessor', 'SwapFlyProcessor', 'LeverageSwapCurveProcessor', 'LeverageSwapFlyProcessor']


class LinearRateProcessor(Processor):
    grammar = 'linear_rate'


class CrossCurrencySwapProcessor(SingleSizeProcessorMixin,
                                 LinearRateProcessor):
    product_type = 'cross_currency_swap'
    attribute_names = ('currencies', 'is_mtm', 'start_time', 'end_time',
                       'strike', 'float_freq', 'size', 'is_risk')


class FixFloatSwapProcessor(SingleSizeProcessorMixin,
                            LinearRateProcessor):
    product_type = 'fix_float_swap'
    attribute_names = ('currency', 'start_time', 'end_time', 'strike',
                       'float_freq', 'fixed_daycount', 'size', 'is_risk')


class FraProcessor(SingleSizeProcessorMixin,
                   LinearRateProcessor):
    product_type = 'fra'
    attribute_names = ('currency', 'start_time', 'end_time',
                       'is_imm', 'strike', 'size')


class TenorBasisSwapProcessor(SingleSizeProcessorMixin,
                              LinearRateProcessor):
    product_type = 'tenor_basis_swap'
    attribute_names = ('currency', 'start_time', 'end_time', 'strike',
                       'float_freq', 'fixed_daycount', 'size', 'is_risk')


class SwapCurveProcessor(MultiSizeProcessorMixin,
                         LinearRateProcessor):
    product_type = 'swap_curve'
    attribute_names = ('currency', 'start_time', 'end_time', 'strike',
                       'float_freq', 'fixed_daycount', 'size', 'is_risk')


class SwapFlyProcessor(MultiSizeProcessorMixin,
                       LinearRateProcessor):
    product_type = 'swap_fly'
    attribute_names = ('currency', 'start_time', 'end_time', 'strike',
                       'float_freq', 'fixed_daycount', 'size', 'is_risk')


class LeverageSwapCurveProcessor(MultiSizeProcessorMixin,
                                 LeverageScheduleProcessorMixin,
                                 LinearRateProcessor):
    product_type = 'leverage_swap_curve'
    attribute_names = ('currency', 'start_time', 'end_time', 'strike',
                       'float_freq', 'fixed_daycount', 'size', 'is_risk')


class LeverageSwapFlyProcessor(MultiSizeProcessorMixin,
                               LeverageScheduleProcessorMixin,
                               LinearRateProcessor):
    product_type = 'leverage_swap_fly'
    attribute_names = ('currency', 'start_time', 'end_time', 'strike',
                       'float_freq', 'fixed_daycount', 'size', 'is_risk')


processors_registry[CrossCurrencySwapProcessor.to_key()] = CrossCurrencySwapProcessor
processors_registry[FixFloatSwapProcessor.to_key()] = FixFloatSwapProcessor
processors_registry[FraProcessor.to_key()] = FraProcessor
processors_registry[TenorBasisSwapProcessor.to_key()] = TenorBasisSwapProcessor
processors_registry[SwapCurveProcessor.to_key()] = SwapCurveProcessor
processors_registry[SwapFlyProcessor.to_key()] = SwapFlyProcessor
processors_registry[LeverageSwapCurveProcessor.to_key()] = LeverageSwapCurveProcessor
processors_registry[LeverageSwapFlyProcessor.to_key()] = LeverageSwapFlyProcessor
