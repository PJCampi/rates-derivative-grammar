from enum import Enum
from typing import TypeVar, ClassVar, Type

from bidict import bidict
from lark import Token

from ._base import TokenConverter, TokenConversionError

__all__ = ["EnumConverter", "BooleanConverter", "FloatConverter", "DictConverter"]

E = TypeVar("E", bound=Enum)
T = TypeVar("T")


class EnumConverter(TokenConverter[E]):
    enum: ClassVar[Type[E]]

    @classmethod
    def from_token(cls, node: Token) -> E:
        return cls.enum[node]

    @classmethod
    def to_token(cls, name: str, obj: E) -> Token:
        if not isinstance(obj, cls.enum):
            raise TokenConversionError(f"{cls.__qualname__} can only format instances of {cls.enum.__qualname__}.")
        return Token(name, obj.name)


class BooleanConverter(TokenConverter[bool]):
    flag: ClassVar[str]

    @classmethod
    def from_token(cls, node: Token) -> bool:
        return True

    @classmethod
    def to_token(cls, name: str, obj: bool) -> Token:
        if not isinstance(obj, bool):
            raise TokenConversionError(f"{cls.__qualname__} can format booleans.")

        if obj:
            return Token(name, cls.flag)
        else:
            return Token(name, "")


class FloatConverter(TokenConverter[float]):
    scaling_factor: ClassVar[float]
    formatting: ClassVar[str]

    @classmethod
    def from_token(cls, node: Token) -> float:
        return float(node.value) / cls.scaling_factor

    @classmethod
    def to_token(cls, name: str, obj: float) -> Token:
        if not isinstance(obj, (float, int)):
            raise TokenConversionError(f"{cls.__qualname__} can only format floating point numbers.")
        return Token(name, f"{obj * cls.scaling_factor:{cls.formatting}}")


class DictConverter(TokenConverter[T]):
    mapping: ClassVar[bidict]

    @classmethod
    def from_token(cls, node: Token) -> T:
        try:
            return cls.mapping[node]
        except KeyError:
            raise TokenConversionError(f"Unknown token: {node}. Possible values: {list(cls.mapping.keys())}.")

    @classmethod
    def to_token(cls, name: str, obj: T) -> Token:
        try:
            return Token(name, cls.mapping.inv[obj])
        except KeyError:
            raise TokenConversionError(f"Unknown value: {obj}. Possible values: {list(cls.mapping.values())}.")
