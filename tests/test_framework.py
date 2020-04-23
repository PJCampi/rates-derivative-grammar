from itertools import chain
from operator import attrgetter

from lark import Lark, Token
from lark.grammar import NonTerminal
import pytest

from rates_derivative_grammar.parsers import AssetClassFormatter
from rates_derivative_grammar.processing._generic import SingleSizeProcessorMixin, MultiSizeProcessorMixin, LeverageScheduleProcessorMixin, RelativeStrikeProcessorMixin
from rates_derivative_grammar.visitors import get_tokens_dict
from rates_derivative_grammar.transformers import FromTokenConversionTransformer, RenameNodeTransformer
from rates_derivative_grammar.conversion._base import TokenConverter, TokenConverterRegistry
from rates_derivative_grammar.grammar_analysis import Grammar
from rates_derivative_grammar.utils import make_parser


class FooConverter(TokenConverter[str]):

    name = 'FOO'

    @classmethod
    def from_token(cls, token: Token) -> str:
        return token[::-1]

    @classmethod
    def to_token(cls, name: str, obj: str) -> Token:
        return Token(name, obj[::-1])


TokenConverterRegistry.register(FooConverter)


class TestParsers:

    @classmethod
    def setup_class(cls):
        grammar = '''
        start: FOO bar baz
        
        
        baz: bar BAZ
        bar: BAR
        
        FOO: "foo"
        BAR: "bar"
        BAZ: "baz"
        '''
        cls.grammar = grammar
        cls.lark = Lark(grammar)
        cls.tree = Lark(grammar).parse('foobarbarbaz')

    @pytest.mark.parametrize('to_parse, expected',
                             [
                                 ('foobarbarbaz', {'foo': 'foo', 'bar': 'bar', 'baz': {'bar': 'bar', 'baz': 'baz'}})
                             ])
    def test_get_tokens_dict(self, to_parse, expected):
        tree = self.lark.parse(to_parse)
        assert get_tokens_dict(tree)['start'] == expected

    @pytest.mark.parametrize('to_parse, expected',
                             [
                                 ('foobarbarbaz',  {'foo': 'oof', 'bar': 'bar', 'baz': {'bar': 'bar', 'baz': 'baz'}})
                             ])
    def test_token_converter(self, to_parse, expected):
        tree = self.lark.parse(to_parse)
        transformer = FromTokenConversionTransformer()
        new_tree = transformer.transform(tree)
        assert get_tokens_dict(new_tree)['start'] == expected

    @pytest.mark.parametrize('to_parse, expected',
                             [
                                 ('foobarbarbaz',  {'foo': 'foo', 'bur': 'bar', 'buz': {'bur': 'bar', 'buz': 'baz'}})
                             ])
    def test_rename_node_transformer(self, to_parse, expected):
        tree = self.lark.parse(to_parse)
        transformer = RenameNodeTransformer(lambda s: s.lower().replace('a', 'u') if s != 'start' else s)
        new_tree = transformer.transform(tree)
        assert get_tokens_dict(new_tree)['start'] == expected


class TestGrammarAnalysis:

    @pytest.mark.parametrize('start, expected, to_parse',
                             [
                                 ('a', ['<a : A>'], ['A']),
                                 ('a_or_b', ['<a_or_b : a>', '<a_or_b : b>', '<a : A>', '<b : B>'], ['B']),
                                 ('start', ['<start : a_or_b b>', '<a_or_b : a>', '<a_or_b : b>', '<a : A>', '<b : B>'], ['B', 'B']),
                             ])
    def test_get_rules(self, start, expected, to_parse):
        grammar = '''
        start: a_or_b b
        a_or_b: a | b
        b: B
        a: A
        
        A: "A"
        B: "B"
        '''

        lark = Lark(grammar)
        grammar = Grammar(lark.rules)
        rules = list(grammar.get_rules(start))
        assert sorted(str(rule) for rule in rules) == sorted(expected)

        parser = make_parser(rules, start)
        parser.parse((Token(itm, '') for itm in to_parse), start=start)

    @pytest.mark.parametrize('to_sort, sorted_',
                             [
                                 (['b', 'A', 'c'], ['A', 'b', 'c']),
                                 (['b_and_a', 'a', 'b', 'A', 'start'], ['start', 'a', 'A', 'b_and_a', 'b'])
                             ])
    def test_sort(self, to_sort, sorted_):
        grammar = '''
        start: a? b_and_a c
        a: A
        b_and_a: b a
        b: B
        c: C

        A: "A"
        B: "B"
        C: "C"
        '''
        lark = Lark(grammar)
        grammar = Grammar(Grammar(lark.rules).get_rules('start'))
        assert grammar.sort(to_sort) == sorted_

    @pytest.mark.parametrize('to_trim, expected, to_parse',
                             [
                                 (['b'], ['<start : a_or_b b>', '<a_or_b : a>', '<a_or_b : b>', '<a : A>'], [('A', 'A'), ('b', 'B')]),
                                 (['a', 'b'], ['<start : a_or_b b>', '<a_or_b : a>', '<a_or_b : b>'], [('a', 'A'), ('b', 'B')]),
                                 (['A', 'other_b'], ['<start : a_or_b b>', '<a_or_b : a>', '<a_or_b : b>', '<a : A>', '<b : other_b>'], [('A', 'A'), ('other_b', 'B')]),
                             ])
    def test_trim(self, to_trim, expected, to_parse):
        grammar = '''
        start: a_or_b b
        a_or_b: a | b
        b: other_b
        
        a: A
        other_b: B
        
        A: "A"
        B: "B"
        '''
        lark = Lark(grammar)
        grammar = Grammar(lark.rules)
        rules = list(grammar.trim(to_trim))
        assert sorted(str(rule) for rule in rules) == sorted(expected)

        parser = make_parser(rules)
        parser.parse((Token(name, val) for name, val in to_parse), start="start")

    def test_expand_inline_rules(self):
        grammar = '''
        start: ab_or_b b
        ab_or_b: _a_or_b__and_b | b
        _a_or_b__and_b: a_or_b _b
        ?a_or_b: _a | _b
        _a: A
        _b: b
        b: B

        A: "A"
        B: "B"
        '''
        lark = Lark(grammar)
        grammar = Grammar(lark.rules)
        rules = [str(rule) for rule in grammar.expand_inline_rules()]
        assert rules == ['<start : ab_or_b b>', '<ab_or_b : b>', '<ab_or_b : b b>', '<ab_or_b : A b>', '<b : B>']


class TestProcessors:
    @pytest.mark.parametrize('size, expected',
                             [
                                 (100000000, [Token('NOTIONAL_NUMBER', 100.), Token('NOTIONAL_UNIT', 1_000_000.)]),
                                 (12153, [Token('NOTIONAL_NUMBER', 12.153), Token('NOTIONAL_UNIT', 1_000.)]),
                                 (12.1, [Token('NOTIONAL_NUMBER', 12.1)]),
                              ])
    def test_single_size_post_processors(self, size, expected):
        nodes = AssetClassFormatter._make_attributes_nodes({'size': size}, [NonTerminal('size')])
        assert list(SingleSizeProcessorMixin.pre_process(nodes))[0].children == expected

    @pytest.mark.parametrize('size, expected',
                             [
                                 (100000000, [Token('NOTIONAL_NUMBER', 100.), Token('NOTIONAL_UNIT', 1_000_000.)]),
                                 ([1000, 12000], [Token('NOTIONAL_NUMBER', 1.), Token('NOTIONAL_UNIT', 1_000.), Token('NOTIONAL_NUMBER', 12.), Token('NOTIONAL_UNIT', 1_000.)]),
                                 ([12.153, 12153000], [Token('NOTIONAL_NUMBER', 12.153), Token('NOTIONAL_NUMBER', 12.153), Token('NOTIONAL_UNIT', 1_000_000.)])
                              ])
    def test_multi_size_post_processors(self, size, expected):
        nodes = AssetClassFormatter._make_attributes_nodes({'size': size}, [NonTerminal('size')])
        assert list(MultiSizeProcessorMixin.pre_process(nodes))[0].children == expected

    @pytest.mark.parametrize('start_times, end_times, expected',
                             [
                                 (['5Y'], ['10Y'], [Token('UNKNOWN', '5Y'), Token('UNKNOWN', '10Y')]),
                                 (['1Y', '2Y'], ['3Y', '4Y'], [Token('UNKNOWN', '1Y'), Token('UNKNOWN', '3Y'), Token('UNKNOWN', '2Y'), Token('UNKNOWN', '4Y')]),
                                 (['1Y', '2Y', '5Y'], ['3Y', '4Y', '6Y'], [Token('UNKNOWN', '1Y'), Token('UNKNOWN', '3Y'), Token('UNKNOWN', '2Y'), Token('UNKNOWN', '4Y'),  Token('UNKNOWN', '5Y'),  Token('UNKNOWN', '6Y')]),

                             ])
    def test_leverage_schedule_post_processors(self, start_times, end_times, expected):
        nodes = AssetClassFormatter._make_attributes_nodes({'start_time': start_times, 'end_time': end_times}, [NonTerminal('start_time'), NonTerminal('end_time')])
        assert list(chain.from_iterable(map(attrgetter('children'), LeverageScheduleProcessorMixin.pre_process(nodes)))) == expected

    @pytest.mark.parametrize('strike, expected',
                             [
                                 ([1.], [Token('IS_RELATIVE', True), Token('FULL_STRIKE_BP', 1.)]),
                             ])
    def test_leverage_schedule_post_processors(self, strike, expected):
        nodes = AssetClassFormatter._make_attributes_nodes({'IS_RELATIVE': True, 'strike': strike}, [NonTerminal('strike')])
        assert list(RelativeStrikeProcessorMixin.pre_process(nodes))[0].children == expected
