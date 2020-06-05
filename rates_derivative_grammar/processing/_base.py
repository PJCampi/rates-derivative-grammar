from typing import Dict, Type, Iterable, Tuple

from lark import Transformer

from ..utils import PATH_DELIMITER, Node, to_name


__all__ = ["Processor", "processors_registry", "to_processor_key"]


def to_processor_key(asset_class: str, product_type: str) -> str:
    return f"{asset_class}{PATH_DELIMITER}{product_type}"


class Processor(Transformer):
    """
    Used to reduce the parsed tree: for example [notional, notional_unit] can be reduced to [notional * unit_multiplier}
    The pre-process method does the opposite to formatted attributes before they can be converted to a tree that the
    grammar parses.
    """

    grammar = ""
    product_type = ""
    attribute_names: Tuple[str, ...] = tuple()

    @classmethod
    def to_key(cls):
        return to_processor_key(cls.grammar, cls.product_type)

    @classmethod
    def pre_process(cls, attributes: Iterable[Node]) -> Iterable[Node]:
        for attribute in sorted(attributes, key=lambda t: cls.attribute_names.index(to_name(t).lower())):
            yield attribute


processors_registry: Dict[str, Type[Processor]] = {}
