# pylint: disable=no-member
from functools import reduce
from itertools import chain
from operator import mul, attrgetter
from typing import Iterable, List, Tuple

from lark import Tree, Token

from ._base import Processor
from ..conversion import NotionalUnitConverter, NotionalNumberConverter, IsRelativeConverter, FullStrikeBpConverter
from ..utils import Node, to_name

__all__ = [
    "SingleSizeProcessorMixin",
    "MultiSizeProcessorMixin",
    "RelativeStrikeProcessorMixin",
    "LeverageScheduleProcessorMixin",
]


class BaseSizeProcessor:
    @staticmethod
    def make_size_tree(attribute_name: str, children: List[Node]) -> Tree:
        if "notional_unit" in list(map(attrgetter("type"), children)):
            children = [Token("notional", reduce(mul, map(attrgetter("value"), children)))]
        return Tree(attribute_name, children)

    @staticmethod
    def format_size(size: Token) -> List[Token]:
        for unit in NotionalUnitConverter.mapping.inv:
            if abs(int(size.value) / unit) >= 1:
                return [Token(NotionalNumberConverter.name, size.value / unit), Token(NotionalUnitConverter.name, unit)]
        else:
            return [Token(NotionalNumberConverter.name, size.value)]


class SingleSizeProcessorMixin(Processor, BaseSizeProcessor):
    attribute_names: Tuple[str, ...] = ("size",)

    def size(self, children: List[Node]) -> Tree:
        return self.make_size_tree("size", children)

    @classmethod
    def pre_process(cls, attributes: Iterable[Tree]) -> Iterable[Tree]:
        for attribute in super().pre_process(attributes):
            if to_name(attribute) == "size":
                attribute.children = cls.format_size(attribute.children[0])
            yield attribute


class MultiSizeProcessorMixin(Processor, BaseSizeProcessor):
    attribute_names: Tuple[str, ...] = ("size",)

    def swap_size(self, children: List[Node]) -> Tree:
        return self.make_size_tree("swap_size", children)

    @classmethod
    def pre_process(cls, attributes: Iterable[Tree]) -> Iterable[Tree]:
        for attribute in super().pre_process(attributes):
            if to_name(attribute) == "size":
                children = []
                for size in attribute.children:
                    children.extend(cls.format_size(size))
                attribute.children = children
            yield attribute


class RelativeStrikeProcessorMixin(Processor):
    attribute_names: Tuple[str, ...] = ("is_relative", "strike")

    def strike(self, children: List[Node]) -> Tree:
        if "is_relative" in map(attrgetter("type"), children):
            return Tree("strike_info", [Tree("is_relative", [children.pop(0)]), Tree("strike", children)])
        return Tree("strike", children)

    @classmethod
    def pre_process(cls, attributes: Iterable[Tree]) -> Iterable[Tree]:
        iterable = iter(super().pre_process(attributes))
        for attribute in iterable:
            if to_name(attribute) == "IS_RELATIVE":
                strike = next(iterable)
                if to_name(strike) != "strike":
                    raise ValueError("'is_relative' attribute must be immediately followed by 'strike' attribute.")
                yield Tree(
                    "strike",
                    [
                        Token(IsRelativeConverter.name, attribute.value),
                        Token(FullStrikeBpConverter.name, strike.children[0].value),
                    ],
                )
            else:
                yield attribute


class LeverageScheduleProcessorMixin(Processor):
    attribute_names: Tuple[str, ...] = ("start_time", "end_time")

    def schedule(self, children: List[Node]) -> Tree:
        start_times: List[Token] = []
        end_times: List[Token] = []
        for child in children:
            if child.data == "start_time":
                start_times.extend(child.children)
            elif child.data == "end_time":
                end_times.extend(child.children)
            else:
                raise NotImplementedError()
        children = [Tree("start_time", start_times), Tree("end_time", end_times)]
        return Tree("schedule", children)

    @classmethod
    def pre_process(cls, attributes: Iterable[Tree]) -> Iterable[Tree]:
        iterable = iter(super().pre_process(attributes))
        for attribute in iterable:
            if to_name(attribute) == "start_time":
                start_times = map(lambda t: Tree("start_time", [t]), attribute.children)
                end_times = next(iterable)

                if to_name(end_times) != "end_time":
                    raise ValueError("'start_time' attribute must be immediately followed by 'end_time' attribute.")
                end_times = map(lambda t: Tree("end_time", [t]), end_times.children)

                for tree in chain.from_iterable(zip(start_times, end_times)):
                    yield tree
            else:
                yield attribute
