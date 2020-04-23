from datetime import datetime, date
from typing import ClassVar

from bidict import bidict
from lark import Token

from ._base import TokenConverter, TokenConversionError
from ._generic import BooleanConverter, FloatConverter, DictConverter


__all__ = ['DateConverter', 'MonthIntConverter', 'YearIntConverter', 'NotionalUnitConverter', 'IsRiskConverter',
           'TenorFreqConverter', 'StrikeBpConverter', 'FullStrikeBpConverter', 'StrikePctConverter',
           'FullStrikePctConverter', 'IsRelativeConverter', 'NotionalNumberConverter']

GRAMMAR = 'shared'


class DateConverter(TokenConverter[date]):

    grammar = 'dates'
    name = 'DATE'
    format = '%d%b%y'

    @classmethod
    def from_token(cls, token: Token) -> date:
        try:
            return datetime.strptime(token, cls.format).date()
        except Exception as e:
            raise TokenConversionError(str(e))

    @classmethod
    def to_token(cls, name: str, obj: date) -> Token:
        if not isinstance(obj, date):
            raise TokenConversionError(f'{cls.__qualname__} can only format dates.')
        return Token(name, obj.strftime(cls.format).upper().lstrip('0'))


class TenorIntConverter(TokenConverter[str]):

    tenor_unit: ClassVar[str]

    @classmethod
    def from_token(cls, token: Token) -> str:
        return f'{token.value}{cls.tenor_unit}'

    @classmethod
    def to_token(cls, name: str, obj: str) -> Token:
        if not isinstance(obj, str):
            raise TokenConversionError(f'{cls.__qualname__} can only format strings.')
        return Token(name, obj[:-len(cls.tenor_unit)])


class MonthIntConverter(TenorIntConverter):

    grammar = 'tenors'
    name = 'MONTH_INT'
    tenor_unit = 'M'


class YearIntConverter(TenorIntConverter):

    grammar = 'tenors'
    name = 'YEAR_INT'
    tenor_unit = 'Y'


class NotionalUnitConverter(DictConverter[float]):

    grammar = GRAMMAR
    name = 'NOTIONAL_UNIT'
    mapping = bidict({'T': 1e12, 'BN': 1e9, 'MM': 1e6, 'K': 1e3})


class IsRiskConverter(BooleanConverter):

    grammar = GRAMMAR
    name = 'IS_RISK'
    flag = 'R'
    

class TenorFreqConverter(TokenConverter[str]):

    grammar = GRAMMAR
    name = 'TENOR_FREQ'

    @classmethod
    def from_token(cls, token: Token) -> str:
        return token.value.replace('S', 'M')

    @classmethod
    def to_token(cls, name: str, obj: str) -> Token:
        if not isinstance(obj, str):
            raise TokenConversionError(f'{cls.__qualname__} can only format strings.')
        return Token(name, obj.replace('M', 'S'))
    

class StrikeBpConverter(FloatConverter):

    grammar = GRAMMAR
    name = 'STRIKE_BP'
    scaling_factor = 10_000
    formatting = '.4g'


class FullStrikeBpConverter(StrikeBpConverter):

    name = 'FULL_STRIKE_BP'


class StrikePctConverter(FloatConverter):

    grammar = GRAMMAR
    name = 'STRIKE_PCT'
    scaling_factor = 100
    formatting = '.6g'


class FullStrikePctConverter(StrikePctConverter):
    
    name = 'FULL_STRIKE_PCT'


class IsRelativeConverter(BooleanConverter):

    grammar = GRAMMAR
    name = 'IS_RELATIVE'
    flag = 'A'


class NotionalNumberConverter(FloatConverter):
    grammar = GRAMMAR
    name = 'NOTIONAL_NUMBER'
    scaling_factor = 1

    @classmethod
    def to_token(cls, name: str, obj: float) -> Token:

        if not isinstance(obj, (int, float)):
            raise TokenConversionError(f'{cls.__qualname__} can only format floating point numbers.')

        # decimals to match
        decimals = [i / 10 for i in range(10)] + [0.25, 0.5, 0.75]

        # get closest decimal
        integer, decimal = int(obj), obj - int(obj)
        distances = [(abs(decimal) - itm) ** 2 for itm in decimals]
        decimal = (-1 if decimal < 0 else 1) * decimals[distances.index(min(distances))]

        # make token
        return Token(name, f'{integer + decimal}'.replace('.0', ''))
