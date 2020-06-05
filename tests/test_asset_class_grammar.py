from datetime import date

import pytest

from rates_derivative_grammar import AssetClassParser, AssetClassFormatter
from rates_derivative_grammar.custom_types import Currency, DayCount, SettlementMethod, SwaptionStrategy, CapFloorStrategy


class TestLinearRateGrammar:

    grammar = 'linear_rate'

    @classmethod
    def setup_class(cls):
        cls.parser = AssetClassParser(cls.grammar)
        cls.formatter = AssetClassFormatter(cls.grammar)

    @pytest.mark.parametrize('node', ['fix_float_swap'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 ('10Y 1', {'end_time': '10Y', 'size': 1.0}),
                                 ('7Y5Y -100m', {'start_time': '7Y', 'end_time': '5Y', 'size': -100_000_000}),
                                 ('1sep2715sep37 2 6s', {'start_time': date(2027, 9, 1), 'end_time': date(2037, 9, 15), 'strike': 0.02, 'float_freq': '6M'}),
                                 ('15sep3725Y 2 2', {'start_time': date(2037, 9, 15), 'end_time': '25Y', 'strike': 0.02, 'size': 2}),
                                 ('7Y 0.4 6s 1b', {'end_time': '7Y', 'strike': 0.004, 'float_freq': '6M', 'size': 1_000_000_000}),
                                 ('10Y10Y 6s', {'start_time': '10Y', 'end_time': '10Y', 'float_freq': '6M'}),
                                 ('M8U8 1d 100m', {'start_time': 'M8', 'end_time': 'U8', 'float_freq': '1D', 'size': 100_000_000}),
                                 ('EUR 4.25Y 3s 100m', {'currency': Currency.EUR, 'end_time': '4.25Y', 'float_freq': '3M', 'size': 100_000_000}),
                                 ('EUR 10Y 97.25kr', {'currency': Currency.EUR, 'end_time': '10Y', 'size': 97_250, 'is_risk': True}),
                                 ('EUR 1Y23M 1d 100m', {'currency': Currency.EUR, 'start_time': '1Y', 'end_time': '23M', 'float_freq': '1D', 'size': 100_000_000}),
                                 ('EUR 1W 1 1d', {'currency': Currency.EUR, 'end_time': '1W', 'strike': 0.01, 'float_freq': '1D'}),
                                 ('EUR 0D 1d', {'currency': Currency.EUR, 'end_time': '0D', 'float_freq': '1D'}),
                                 ('EUR 1D 1d', {'currency': Currency.EUR, 'end_time': '1D', 'float_freq': '1D'}),
                                 ('EUR 5Y10Y 0.1 1S ACT365 100KR', {'currency': Currency.EUR, 'start_time': '5Y', 'end_time': '10Y', 'strike': 0.001, 'float_freq': '1M', 'fixed_daycount': DayCount.ACT365, 'size': 100_000, 'is_risk': True}),
                                 ('10y', {'end_time': '10Y'}),
                                 ('dkk 10y', {'currency': Currency.DKK, 'end_time': '10Y'}),
                                 ('5y5y', {'start_time': '5Y', 'end_time': '5Y'}),
                                 ('2.5y5y', {'start_time': '2.5Y', 'end_time': '5Y'}),
                                 ('u8u9', {'start_time': 'U8', 'end_time': 'U9'}),
                                 ('4apr1910y 100m', {'start_time': date(2019, 4, 4), 'end_time': '10Y', 'size': 100_000_000}),
                                 ('10y -10kr',  {'end_time': '10Y', 'size': -10_000, 'is_risk': True}),
                                 ('EUR 5Y5Y 3s -50.1kr', {'currency': Currency.EUR, 'start_time': '5Y', 'end_time': '5Y', 'float_freq': '3M', 'size': -50_100, 'is_risk': True}),
                                 ('10y 6s', {'end_time': '10Y', 'float_freq': '6M'}),
                                 ('2y5y 0.5', {'start_time': '2Y', 'end_time': '5Y', 'size': 0.5}),
                             ])
    def test_swap_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        assert self.formatter.format(node, values) == to_parse.upper()

    @pytest.mark.parametrize('node', ['fra'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 ('3x6 100m', {'start_time': '3M', 'end_time': '6M', 'size': 100_000_000}),
                                 ('3x6i -100m', {'start_time': '3M', 'end_time': '6M', 'is_imm': True, 'size': -100_000_000}),
                                 ('3x6', {'start_time': '3M', 'end_time': '6M'}),
                                 ('dkk 3x6', {'currency': Currency.DKK, 'start_time': '3M', 'end_time': '6M'}),
                                 ('3x6i', {'start_time': '3M', 'end_time': '6M', 'is_imm': True}),
                                 ('DKK 3x6i -0.36', {'currency': Currency.DKK, 'start_time': '3M', 'end_time': '6M', 'is_imm': True, 'strike': -0.0036}),
                                 ('3x6i -100m', {'start_time': '3M', 'end_time': '6M', 'is_imm': True, 'size': -100_000_000}),
                                 ('3x6i 10k', {'start_time': '3M', 'end_time': '6M', 'is_imm': True, 'size': 10_000}),
                                 ('DKK 11x23 0.12 125.1m', {'currency': Currency.DKK, 'start_time': '11M', 'end_time': '23M', 'strike': 0.0012, 'size': 125_100_000}),
                                 ('3x9 2', {'start_time': '3M', 'end_time': '9M', 'size': 2.0}),
                             ])
    def test_fra_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        assert self.formatter.format(node, values) == to_parse.upper()

    @pytest.mark.parametrize('node', ['tenor_basis_swap'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 ('10Y 2 3s6s', {'end_time': '10Y', 'strike': 0.0002, 'float_freq': ['3M', '6M']}),
                                 ('EUR 5Y10Y 2/1 1d6s ACT365 100KR', {'currency': Currency.EUR, 'start_time': '5Y', 'end_time': '10Y', 'strike': [0.02, 0.0001], 'float_freq': ['1D', '6M'], 'fixed_daycount': DayCount.ACT365, 'size': 100_000, 'is_risk': True}),
                                 ('10Y 1d3s', {'end_time': '10Y', 'float_freq': ['1D', '3M']}),
                                 ('sek 10Y 1d3s', {'currency': Currency.SEK, 'end_time': '10Y', 'float_freq': ['1D', '3M']}),
                                 ('10Y 8.5 3s6s', {'end_time': '10Y', 'strike': 0.00085, 'float_freq': ['3M', '6M']}),
                                 ('2y10y 1.095/8.5 3s6s', {'start_time': '2Y', 'end_time': '10Y', 'strike': [0.01095, 0.00085], 'float_freq': ['3M', '6M']}),
                                 ('10Y 3s6s 100m', {'end_time': '10Y', 'float_freq': ['3M', '6M'], 'size': 100_000_000}),
                                 ('5y10y 3s6s 100m', {'start_time': '5Y', 'end_time': '10Y', 'float_freq': ['3M', '6M'], 'size': 100_000_000}),
                                 ('10y 3s6s 10kr', {'end_time': '10Y', 'float_freq': ['3M', '6M'], 'size': 10_000, 'is_risk': True}),
                             ])
    def test_tenor_swap_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        assert self.formatter.format(node, values) == to_parse.upper()

    @pytest.mark.parametrize('node', ['cross_currency_swap'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 ('eurusd 5y', {'currencies': [Currency.EUR, Currency.USD], 'end_time': '5Y'}),
                                 ('sekeur 16sep195y', {'currencies': [Currency.SEK, Currency.EUR], 'start_time': date(2019, 9, 16), 'end_time': '5Y'}),
                                 ('dkksek mtm 5y10y -100m', {'currencies': [Currency.DKK, Currency.SEK], 'is_mtm': True, 'start_time': '5Y', 'end_time': '10Y', 'size': -100_000_000}),
                             ])
    def test_xccy_swap_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        assert self.formatter.format(node, values) == to_parse.upper()

    @pytest.mark.parametrize('node', ['swap_curve'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 ('5s10s 65.5', {'end_time': ['5Y', '10Y'], 'size': 65.5}),
                                 ('EUR 5Y 5s10s 2/1 6s ACT365 1M/500KR', {'currency': Currency.EUR, 'start_time': '5Y', 'end_time': ['5Y', '10Y'], 'strike': [0.02, 0.0001], 'float_freq': '6M', 'fixed_daycount': DayCount.ACT365, 'size': [1_000_000, 500_000], 'is_risk': True}),
                                 ('5s10s',  {'end_time': ['5Y', '10Y']}),
                                 ('3oct18 3s7s',  {'start_time': date(2018, 10, 3), 'end_time': ['3Y', '7Y']}),
                                 ('5s10s 100m', {'end_time': ['5Y', '10Y'], 'size': 100_000_000}),
                                 ('sek 5s10s -100m', {'currency': Currency.SEK, 'end_time': ['5Y', '10Y'], 'size': -100_000_000}),
                                 ('5s10s -193.4m/100m', {'end_time': ['5Y', '10Y'], 'size': [-193_400_000, 100_000_000]}),
                                 ('5s10s 61.5 3s', {'end_time': ['5Y', '10Y'], 'strike': 0.00615, 'float_freq': '3M'}),
                                 ('5s10s 3s',  {'end_time': ['5Y', '10Y'], 'float_freq': '3M'}),
                                 ('5s10s 0.426/61.5 3s',  {'end_time': ['5Y', '10Y'], 'strike': [0.00426, 0.00615], 'float_freq': '3M'}),
                             ])
    def test_curve_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        assert self.formatter.format(node, values) == to_parse.upper()

    @pytest.mark.parametrize('node', ['leverage_swap_curve'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 # ('H01YsH21Ys', {'start_time': ['H0', 'H2'], 'end_time': ['1Y', '1Y']}),
                                 ('EUR 1jan195Ys30mar1910Ys 0.5/2 1d ACT365 1.2M', {'currency': Currency.EUR, 'start_time': [date(2019, 1, 1), date(2019, 3, 30)], 'end_time': ['5Y', '10Y'], 'strike': [0.005, 0.0002], 'float_freq': '1D', 'fixed_daycount': DayCount.ACT365, 'size': 1_200_000}),
                                 ('2y2ys4y2ys', {'start_time': ['2Y', '4Y'], 'end_time': ['2Y', '2Y']}),
                                 ('dkk 2y2ys4y2ys', {'currency': Currency.DKK, 'start_time': ['2Y', '4Y'], 'end_time': ['2Y', '2Y']}),
                                 ('2y2ys4y2ys 3s', {'start_time': ['2Y', '4Y'], 'end_time': ['2Y', '2Y'], 'float_freq': '3M'}),
                                 ('2y2ys4y2ys 0.426/61.5', {'start_time': ['2Y', '4Y'], 'end_time': ['2Y', '2Y'], 'strike': [0.00426, 0.00615]}),
                                 ('H02ysH22ys', {'start_time': ['H0', 'H2'], 'end_time': ['2Y', '2Y']}),
                                 ('H02ysH22ys 100m', {'start_time': ['H0', 'H2'], 'end_time': ['2Y', '2Y'], 'size': 100_000_000}),
                                 ('H02ysH22ys 3s 100m/100mr', {'start_time': ['H0', 'H2'], 'end_time': ['2Y', '2Y'], 'float_freq': '3M', 'size': [100_000_000, 100_000_000], 'is_risk': True}),
                                 ('2y1ys4y2ys', {'start_time': ['2Y', '4Y'], 'end_time': ['1Y', '2Y']}),
                                 ('h01ysh22ys', {'start_time': ['H0', 'H2'], 'end_time': ['1Y', '2Y']}),
                                 ('h0h2sh2h4s', {'start_time': ['H0', 'H2'], 'end_time': ['H2', 'H4']}),
                             ])
    def test_leverage_curve_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        assert self.formatter.format(node, values) == to_parse.upper()

    @pytest.mark.parametrize('node', ['swap_fly'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 ('5s7s10s 6s 100m', {'end_time': ['5Y', '7Y', '10Y'], 'float_freq': '6M', 'size': 100_000_000}),
                                 ('EUR 1jan19 5s7s10s 0.5/2/1 1d ACT365 -5K/10.2K/-5KR', {'currency': Currency.EUR, 'start_time': date(2019, 1, 1), 'end_time': ['5Y', '7Y', '10Y'], 'strike': [0.005, 0.0002, 0.01], 'float_freq': '1D', 'fixed_daycount': DayCount.ACT365, 'is_risk': True, 'size': [-5_000, 10_200, -5_000]}),
                                 ('5s7s10s', {'end_time': ['5Y', '7Y', '10Y']}),
                                 ('5oct18 5s7s10s', {'start_time': date(2018, 10, 5), 'end_time': ['5Y', '7Y', '10Y']}),
                                 ('5s7s10s 100m', {'end_time': ['5Y', '7Y', '10Y'], 'size': 100_000_000}),
                                 ('5s7s10s -10kr', {'end_time': ['5Y', '7Y', '10Y'], 'size': -10_000, 'is_risk': True}),
                                 ('5s7s10s -1.99 3s 100m', {'end_time': ['5Y', '7Y', '10Y'], 'strike': -0.000199, 'float_freq': '3M', 'size': 100_000_000}),
                                 ('5s7s10s 3s -69m/100m/-35.9m', {'end_time': ['5Y', '7Y', '10Y'], 'float_freq': '3M', 'size': [-69_000_000, 100_000_000, -35_900_000]}),
                                 ('5s7s10s 2',  {'end_time': ['5Y', '7Y', '10Y'], 'size': 2.0}),
                                 ('5s7s10s 0.11/2/0.5', {'end_time': ['5Y', '7Y', '10Y'], 'strike': [0.0011, 0.0002, 0.005]}),
                             ])
    def test_fly_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        assert self.formatter.format(node, values) == to_parse.upper()

    @pytest.mark.parametrize('node', ['leverage_swap_fly'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 ('3y1ys4y1ys5y1ys 100m', {'start_time': ['3Y', '4Y', '5Y'], 'end_time': ['1Y', '1Y', '1Y'], 'size': 100_000_000}),
                                 ('5y2ys7y2ys10y2ys', {'start_time': ['5Y', '7Y', '10Y'], 'end_time': ['2Y', '2Y', '2Y']}),
                                 ('dkk 5y2ys7y2ys10y2ys', {'currency': Currency.DKK, 'start_time': ['5Y', '7Y', '10Y'], 'end_time': ['2Y', '2Y', '2Y']}),
                                 ('5y2ys7y2ys10y2ys 0.11/2/0.5', {'start_time': ['5Y', '7Y', '10Y'], 'end_time': ['2Y', '2Y', '2Y'], 'strike': [0.0011, 0.0002, 0.005]}),
                                 ('5y2ys7y2ys10y2ys 6s', {'start_time': ['5Y', '7Y', '10Y'], 'end_time': ['2Y', '2Y', '2Y'], 'float_freq': '6M'}),
                                 ('5y2ys7y2ys10y2ys -100m', {'start_time': ['5Y', '7Y', '10Y'], 'end_time': ['2Y', '2Y', '2Y'], 'size': -100_000_000}),
                                 ('5y2ys7y2ys10y2ys -69m/100m/-35.9m', {'start_time': ['5Y', '7Y', '10Y'], 'end_time': ['2Y', '2Y', '2Y'], 'size': [-69_000_000, 100_000_000, -35_900_000]}),
                                 ('5y2ys7y2ys10y2ys 10kr', {'start_time': ['5Y', '7Y', '10Y'], 'end_time': ['2Y', '2Y', '2Y'], 'size': 10_000, 'is_risk': True}),
                                 ('2y1ys4y2ys6y3ys', {'start_time': ['2Y', '4Y', '6Y'], 'end_time': ['1Y', '2Y', '3Y']}),
                                 ('h01ysh22ysh44ys', {'start_time': ['H0', 'H2', 'H4'], 'end_time': ['1Y', '2Y', '4Y']}),
                                 ('h0h2sh2h4sh4h6s', {'start_time': ['H0', 'H2', 'H4'], 'end_time': ['H2', 'H4', 'H6']}),
                             ])
    def test_leverage_fly_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        assert self.formatter.format(node, values) == to_parse.upper()


class TestRatesVolatilityGrammar:

    grammar = 'rates_volatility'

    @classmethod
    def setup_class(cls):
        cls.parser = AssetClassParser(cls.grammar)
        cls.formatter = AssetClassFormatter(cls.grammar)

    @pytest.mark.parametrize('node', ['swaption'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 ('10Y10Y P Cash 100m', {'start_time': '10Y', 'end_time': '10Y', 'contract_type': SwaptionStrategy.PAYER, 'settlement_method': SettlementMethod.CASH_SETTLED_ISDA, 'size': 100_000_000}),
                                 ('Z910Y 1.35393 R Cash -100m', {'start_time': 'Z9', 'end_time': '10Y', 'strike': 0.0135393, 'contract_type': SwaptionStrategy.RECEIVER, 'settlement_method': SettlementMethod.CASH_SETTLED_ISDA, 'size': -100_000_000}),
                                 ('2.25Y2.5Y P', {'start_time': '2.25Y', 'end_time': '2.5Y', 'contract_type': SwaptionStrategy.PAYER}),
                                 ('usd 2.25Y2.5Y P', {'currency': Currency.USD, 'start_time': '2.25Y', 'end_time': '2.5Y', 'contract_type': SwaptionStrategy.PAYER}),
                                 ('10Y10Y 2.04 S', {'start_time': '10Y', 'end_time': '10Y', 'strike': 0.0204, 'contract_type': SwaptionStrategy.STRADDLE}),
                                 ('10Y10Y 2.04 r', {'start_time': '10Y', 'end_time': '10Y', 'strike': 0.0204, 'contract_type': SwaptionStrategy.RECEIVER}),
                                 ('10Y10Y r', {'start_time': '10Y', 'end_time': '10Y', 'contract_type': SwaptionStrategy.RECEIVER}),
                                 ('10Y10Y p 6s', {'start_time': '10Y', 'end_time': '10Y', 'contract_type': SwaptionStrategy.PAYER, 'float_freq': '6M'}),
                                 ('10Y10Y s', {'start_time': '10Y', 'end_time': '10Y', 'contract_type': SwaptionStrategy.STRADDLE}),
                                 ('EUR 13apr195y p', {'currency': Currency.EUR, 'start_time': date(2019, 4, 13), 'end_time': '5Y', 'contract_type': SwaptionStrategy.PAYER}),
                                 ('EUR 10Y10Y p 3s Phys 100m', {'currency': Currency.EUR, 'start_time': '10Y', 'end_time': '10Y', 'contract_type': SwaptionStrategy.PAYER, 'float_freq': '3M', 'settlement_method': SettlementMethod.PHYSICALLY_SETTLED, 'size': 100_000_000}),
                                 ('2y5y p cash', {'start_time': '2Y', 'end_time': '5Y', 'contract_type': SwaptionStrategy.PAYER, 'settlement_method': SettlementMethod.CASH_SETTLED_ISDA}),
                                 ('2y5y a10 p', {'start_time': '2Y', 'end_time': '5Y', 'contract_type': SwaptionStrategy.PAYER, 'strike': 0.001, 'is_relative': True}),
                                 ('2y5y a-10 p', {'start_time': '2Y', 'end_time': '5Y', 'contract_type': SwaptionStrategy.PAYER, 'strike': -0.001, 'is_relative': True}),
                                 ('2y5y p physc', {'start_time': '2Y', 'end_time': '5Y', 'contract_type': SwaptionStrategy.PAYER, 'settlement_method': SettlementMethod.PHYSICALLY_CLEARED_SETTLED}),
                                 ('2y5y p cashasphys', {'start_time': '2Y', 'end_time': '5Y', 'contract_type': SwaptionStrategy.PAYER, 'settlement_method': SettlementMethod.CASH_SETTLED_PRICED_AS_PHYSICAL}),
                             ])
    def test_swaption_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        assert self.formatter.format(node, values) == to_parse.upper()

    @pytest.mark.parametrize('node', ['swaption_strategy'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 ('5Y5Y 100WC 100m', {'start_time': '5Y', 'end_time': '5Y', 'width': 0.01, 'contract_type': SwaptionStrategy.COLLAR, 'size': 100_000_000}),
                                 ('usd 5Y5Y 100WC -100m', {'currency': Currency.USD, 'start_time': '5Y', 'end_time': '5Y', 'width': 0.01, 'contract_type': SwaptionStrategy.COLLAR, 'size': -100_000_000}),
                                 ('2y5y 10ws', {'start_time': '2Y', 'end_time': '5Y', 'width': 0.001, 'contract_type': SwaptionStrategy.STRANGLE}),
                                 ('5Y5Y 0WC 100m', {'start_time': '5Y', 'end_time': '5Y', 'width': 0, 'contract_type': SwaptionStrategy.COLLAR, 'size': 100_000_000}),
                                 ('EUR 5Y5Y 1.25 50WS Cash', {'currency': Currency.EUR, 'start_time': '5Y', 'end_time': '5Y', 'strike': 0.0125, 'width': 0.005, 'contract_type': SwaptionStrategy.STRANGLE, 'settlement_method': SettlementMethod.CASH_SETTLED_ISDA}),
                                 ('5Y5Y 50WS 3s', {'start_time': '5Y', 'end_time': '5Y', 'width': 0.005, 'contract_type': SwaptionStrategy.STRANGLE, 'float_freq': '3M'}),
                                 ('2y2y 100ws Phys', {'start_time': '2Y', 'end_time': '2Y', 'width': 0.01, 'contract_type': SwaptionStrategy.STRANGLE, 'settlement_method': SettlementMethod.PHYSICALLY_SETTLED}),
                                 ('2y2y 100ws PhysC', {'start_time': '2Y', 'end_time': '2Y', 'width': 0.01, 'contract_type': SwaptionStrategy.STRANGLE, 'settlement_method': SettlementMethod.PHYSICALLY_CLEARED_SETTLED}),
                                 ('2y2y 100ws cashasphys', {'start_time': '2Y', 'end_time': '2Y', 'width': 0.01, 'contract_type': SwaptionStrategy.STRANGLE, 'settlement_method': SettlementMethod.CASH_SETTLED_PRICED_AS_PHYSICAL}),
                                 ('2y2y 100ws Phys -10m', {'start_time': '2Y', 'end_time': '2Y', 'width': 0.01, 'contract_type': SwaptionStrategy.STRANGLE, 'settlement_method': SettlementMethod.PHYSICALLY_SETTLED, 'size': -10_000_000}),
                             ])
    def test_swaption_strategy_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        assert self.formatter.format(node, values) == to_parse.upper()

    @pytest.mark.parametrize('node', ['cap_floor'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 ('7Yx12Y C 3s', {'start_time': '7Y', 'end_time': '12Y', 'contract_type': CapFloorStrategy.CAP, 'float_freq': '3M'}),
                                 ('6Mx10Y 0.91 F 6s -100m', {'start_time': '6M', 'end_time': '10Y', 'strike': 0.0091, 'contract_type': CapFloorStrategy.FLOOR, 'float_freq': '6M', 'size': -100_000_000}),
                                 ('EUR 3Mx12M C 6s', {'currency': Currency.EUR, 'start_time': '3M', 'end_time': '12M', 'contract_type': CapFloorStrategy.CAP, 'float_freq': '6M'}),
                                 ('3Mx12M C 3s', {'start_time': '3M', 'end_time': '12M', 'contract_type': CapFloorStrategy.CAP, 'float_freq': '3M'}),
                                 ('usd 3Mx12M C', {'currency': Currency.USD, 'start_time': '3M', 'end_time': '12M', 'contract_type': CapFloorStrategy.CAP}),
                                 ('10Y F 6s 100m', {'end_time': '10Y', 'contract_type': CapFloorStrategy.FLOOR, 'float_freq': '6M', 'size': 100_000_000}),
                                 ('10Y F 3s -10k', {'end_time': '10Y', 'contract_type': CapFloorStrategy.FLOOR, 'float_freq': '3M', 'size': -10_000}),
                                 ('10Y F', {'end_time': '10Y', 'contract_type': CapFloorStrategy.FLOOR}),
                                 ('EUR 0Mx10Y F 6s 100m', {'currency': Currency.EUR, 'start_time': '0M', 'end_time': '10Y', 'contract_type': CapFloorStrategy.FLOOR, 'float_freq': '6M', 'size': 100_000_000}),
                                 ('0Mx10Y C', {'start_time': '0M', 'end_time': '10Y', 'contract_type': CapFloorStrategy.CAP}),
                                 ('0Mx10Y F', {'start_time': '0M', 'end_time': '10Y', 'contract_type': CapFloorStrategy.FLOOR}),
                                 ('0mx12m a1 c', {'start_time': '0M', 'end_time': '12M', 'is_relative': True, 'strike': 0.0001, 'contract_type': CapFloorStrategy.CAP}),
                                 ('3mx5y 1 f', {'start_time': '3M', 'end_time': '5Y', 'strike': 0.01, 'contract_type': CapFloorStrategy.FLOOR}),
                                 ('usd 3mx5y 1 c', {'currency': Currency.USD, 'start_time': '3M', 'end_time': '5Y', 'strike': 0.01, 'contract_type': CapFloorStrategy.CAP}),
                             ])
    def test_cap_floor_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        assert self.formatter.format(node, values) == to_parse.upper()

    @pytest.mark.parametrize('node', ['cap_floor_strategy'])
    @pytest.mark.parametrize('to_parse, values',
                             [
                                 ('6mx10y 50ws', {'start_time': '6M', 'end_time': '10Y', 'width': 0.005, 'contract_type': CapFloorStrategy.STRANGLE}),
                                 ('3mx5y 100wc', {'start_time': '3M', 'end_time': '5Y', 'width': 0.01, 'contract_type': CapFloorStrategy.COLLAR}),
                                 ('3mx2y s', {'start_time': '3M', 'end_time': '2Y', 'contract_type': CapFloorStrategy.STRADDLE}),
                                 ('EUR 3Mx12M 100WC 6s', {'currency': Currency.EUR, 'start_time': '3M', 'end_time': '12M', 'width': 0.01, 'contract_type': CapFloorStrategy.COLLAR, 'float_freq': '6M'}),
                                 ('3Mx12M 50WC 3s', {'start_time': '3M', 'end_time': '12M', 'width': 0.005, 'contract_type': CapFloorStrategy.COLLAR, 'float_freq': '3M'}),
                                 ('10Y 50WS 6s 100m',  {'end_time': '10Y', 'width': 0.005, 'contract_type': CapFloorStrategy.STRANGLE, 'float_freq': '6M', 'size': 100_000_000}),
                                 ('10Y 100WC 3s -10k',  {'end_time': '10Y', 'width': 0.01, 'contract_type': CapFloorStrategy.COLLAR, 'float_freq': '3M', 'size': -10_000}),
                                 ('EUR 0Mx10Y 0WS 6s 100m', {'currency': Currency.EUR, 'start_time': '0M', 'end_time': '10Y', 'width': 0.0, 'contract_type': CapFloorStrategy.STRANGLE, 'float_freq': '6M', 'size': 100_000_000}),
                                 ('0Mx10Y 0WC', {'start_time': '0M', 'end_time': '10Y', 'width': 0.0, 'contract_type': CapFloorStrategy.COLLAR}),
                                 ('0Mx10Y WC', {'start_time': '0M', 'end_time': '10Y', 'contract_type': CapFloorStrategy.COLLAR}),
                                 ('0Mx10Y 0WS', {'start_time': '0M', 'end_time': '10Y', 'width': 0.0, 'contract_type': CapFloorStrategy.STRANGLE}),
                                 ('usd 3Mx12M S', {'currency': Currency.USD, 'start_time': '3M', 'end_time': '12M', 'contract_type': CapFloorStrategy.STRADDLE}),
                                 ('10Y S', {'end_time': '10Y', 'contract_type': CapFloorStrategy.STRADDLE}),
                                 ('0Mx10Y 0S', {'start_time': '0M', 'end_time': '10Y', 'width': 0, 'contract_type': CapFloorStrategy.STRADDLE}),
                             ])
    def test_cap_floor_strategy_success(self, node, to_parse, values):
        product_type, attributes_dict = self.parser.parse(to_parse.upper())
        assert product_type == node
        assert attributes_dict == values
        #assert self.builder.build(node, values) == to_parse.upper()
