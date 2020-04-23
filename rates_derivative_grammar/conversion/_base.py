from typing import ClassVar, TypeVar, Generic, Dict, Type

from lark import Token

from ..utils import to_path_root, PATH_DELIMITER

__all__ = ['TokenConverterRegistry', 'TokenConverterRegistrationError', 'TokenConversionError']

T = TypeVar('T')


class TokenConverterRegistrationError(KeyError):
    def __init__(self, key):
        super().__init__(key)


class TokenConversionError(ValueError):
    pass


class TokenConverter(Generic[T]):
    # the grammar in which the token is defined
    grammar: ClassVar[str] = ""
    # the name of the token within that grammar
    name: ClassVar[str]

    @classmethod
    def from_token(cls, token: Token) -> T:
        """

        Args:
            token: the token (or "string representation") to convert

        Returns: the value of the token after conversion

        """
        raise NotImplementedError()

    @classmethod
    def to_token(cls, name: str, obj: T) -> Token:
        """

        Args:
            name: the name of the token
            obj: the value of the token after conversion

        Returns: the token (or "string representation")

        """
        raise NotImplementedError()


TTokenConverter = Type[TokenConverter]


class TokenConverterRegistry:
    """
    registers token converters based on their name.
    """

    registry_type: ClassVar[TTokenConverter] = TokenConverter
    match_by_full_path: ClassVar[bool] = False

    _registry: ClassVar[Dict[str, TTokenConverter]] = {}

    @classmethod
    def register(cls, converter: TTokenConverter) -> None:
        cls._registry[cls._converter_to_key(converter)] = converter

    @classmethod
    def get(cls, name: str) -> TTokenConverter:
        type_root = to_path_root(name)
        try:
            match = cls._registry[type_root]
        except KeyError:
            raise TokenConverterRegistrationError(name)

        if cls.match_by_full_path:
            if name == match.name or (match.grammar and name == f'{match.grammar}{PATH_DELIMITER}{match.name}'):
                return match
            raise TokenConverterRegistrationError(name)

        return match

    @classmethod
    def _converter_to_key(cls, converter: TTokenConverter) -> str:
        return f'{converter.name}'
