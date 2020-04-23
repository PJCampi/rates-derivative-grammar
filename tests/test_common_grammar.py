from datetime import date

from lark import Lark
import lark.load_grammar as pth
import pytest

from rates_derivative_grammar import GRAMMAR_PATH
from rates_derivative_grammar.transformers import FromTokenConversionTransformer


# add grammar path to IMPORT_PATHS
if GRAMMAR_PATH not in pth.IMPORT_PATHS:
    pth.IMPORT_PATHS.append(GRAMMAR_PATH)

    
def assert_interpretation(grammar, node, to_parse, value=None, type_=None):
    parser = Lark(f"start: {node}\n%import .common.{grammar}.{node}")
    parsed = parser.parse(to_parse)
    if value or type_:
        converted = FromTokenConversionTransformer().transform(parsed).scan_values(lambda t: True)
        if value:
            values = [tkn.value for tkn in converted]
            assert (values[0] if len(values) == 1 else values) == value
        else:
            types = [tkn.type for tkn in converted]
            assert type_ in types[0]


class TestDatesGrammar:

    grammar = 'dates'

    @pytest.mark.parametrize('node', ['DATE'])
    @pytest.mark.parametrize('to_parse, value',
                             [
                                 ('1MAR19', date(2019, 3, 1)),
                                 ('10MAR19', date(2019, 3, 10)),
                                 ('21MAR19', date(2019, 3, 21)),
                                 ('31MAR19', date(2019, 3, 31))
                             ])
    def test_date_success(self, node, to_parse, value):
        assert_interpretation(self.grammar, node, to_parse, value)

    @pytest.mark.parametrize('node', ['DATE'])
    @pytest.mark.parametrize('to_parse', ['01MAR19', '41MAR19'])
    def test_date_failure(self, node, to_parse):
        with pytest.raises(Exception):
            assert_interpretation(self.grammar, node, to_parse)

    @pytest.mark.parametrize('node', ['QUARTERLY_IMM_DATE'])
    @pytest.mark.parametrize('to_parse', ['MAR09', 'DEC15', 'JUN99'])
    def test_quarterly_imm_date_success(self, node, to_parse):
        assert_interpretation(self.grammar, node, to_parse, to_parse)

    @pytest.mark.parametrize('node', ['QUARTERLY_IMM_DATE'])
    @pytest.mark.parametrize('to_parse', ['FEB09', 'MAR9'])
    def test_quarterly_imm_date_failure(self, node, to_parse):
        with pytest.raises(Exception):
            assert_interpretation(self.grammar, node, to_parse, to_parse)


class TestNumbersGrammar:

    grammar = 'numbers'

    @pytest.mark.parametrize('node', ['QUARTERED_FLOAT'])
    @pytest.mark.parametrize('to_parse', ['15', '5.25', '10.75', '8.5', '0.25'])
    def test_quartered_float_success(self, node, to_parse):
        assert_interpretation(self.grammar, node, to_parse, to_parse)

    @pytest.mark.parametrize('node', ['QUARTERED_FLOAT'])
    @pytest.mark.parametrize('to_parse', ['15.', '5.0', '05.5', '8.2345', '5.25.25'])
    def test_quartered_float_failure(self, node, to_parse):
        with pytest.raises(Exception):
            assert_interpretation(self.grammar, node, to_parse)


class TestTenorsGrammar:

    grammar = 'tenors'

    @pytest.mark.parametrize('node', ['STRICT_TENOR'])
    @pytest.mark.parametrize('to_parse', ['0D', '0B', '5B', '1W', '4W', '1M', '12M', '12M', '15M', '24M', '54M',
                                          '0.75Y', '1.25Y', '20Y', '100Y'])
    def test_strict_tenors_success(self, node, to_parse):
        assert_interpretation(self.grammar, node, to_parse, to_parse)

    @pytest.mark.parametrize('node', ['STRICT_TENOR'])
    @pytest.mark.parametrize('to_parse', ['0W', '25M', '-1Y'])
    def test_strict_tenors_failure(self, node, to_parse):
        with pytest.raises(Exception):
            assert_interpretation(self.grammar, node, to_parse)


class TestSharedGrammar:

    grammar = 'shared'

    @pytest.mark.parametrize('node', ['time'])
    @pytest.mark.parametrize('to_parse, type_',
                             [
                                 ('10.25Y', 'FLOAT_TENOR'),
                                 ('U8', 'QUARTERLY_IMM_TENOR'),
                                 ('15DEC20', 'DATE'),
                             ])
    def test_time_success(self, node, to_parse, type_):
        assert_interpretation(self.grammar, node, to_parse, type_=f'{self.grammar}__{type_}')

    @pytest.mark.parametrize('node', ['_double_years'])
    @pytest.mark.parametrize('to_parse, value',
                             [
                                 ('1S5S', ['1Y', '5Y']), ('20S50S', ['20Y', '50Y']),
                             ])
    def test_double_years_success(self, node, to_parse, value):
        assert_interpretation(self.grammar, node, to_parse, value)

    @pytest.mark.parametrize('node', ['_triple_years'])
    @pytest.mark.parametrize('to_parse, value',
                             [
                                 ('3S5S10S', ['3Y', '5Y', '10Y']), ('20S50S100S', ['20Y', '50Y', '100Y']),
                             ])
    def test_triple_years_success(self, node, to_parse, value):
        assert_interpretation(self.grammar, node, to_parse, value)

    @pytest.mark.parametrize('node', ['basis'])
    @pytest.mark.parametrize('to_parse, value',
                             [('B1D', '1D'), ('B1S', '1M')])
    def test_basis_success(self, node, to_parse, value):
        assert_interpretation(self.grammar, node, to_parse, value)
