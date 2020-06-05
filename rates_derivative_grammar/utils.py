from typing import Union, Iterable, Callable, Optional, Dict

from lark import Token, Tree
from lark.common import ParserConf
from lark.grammar import Rule, Terminal
from lark.parsers.earley import Parser
from lark.parse_tree_builder import ParseTreeBuilder
from lark.utils import classify
from lark.reconstruct import is_discarded_terminal


__all__ = [
    "Node",
    "normalize",
    "denormalize",
    "to_name",
    "to_value",
    "to_path_root",
    "make_parser",
    "PATH_DELIMITER",
    "classify",
    "is_discarded_terminal",
    "is_inline_rule",
]


Node = Union[Token, Tree]

PATH_DELIMITER = "__"


def is_inline_rule(rule: Rule) -> bool:
    return rule.origin.name.startswith("_") or rule.options.expand1 or rule.alias


def normalize(name: str) -> str:
    return name.lower()


def denormalize(name: str) -> str:
    return name.upper()


def to_path_root(name: str) -> str:
    return name.split(PATH_DELIMITER)[-1]


def to_name(node: Node) -> str:

    # get base name
    if isinstance(node, Token):
        return node.type
    if isinstance(node, Tree):
        return node.data
    raise NotImplementedError()


def to_value(node: Node, *, expand_single_child=True):
    # get base name
    if isinstance(node, Token):
        return node.value
    if isinstance(node, Tree):
        results = [to_value(tok) for tok in node.scan_values(lambda tok: True)]
        return results[0] if (expand_single_child and len(results) == 1) else results
    raise NotImplementedError()


def make_parser(
    rules: Iterable[Rule],
    start_symbol: str = "start",
    match: Optional[Callable] = None,
    callbacks: Optional[Dict] = None,
) -> Parser:

    rules = list(rules)

    if not callbacks:
        callbacks = ParseTreeBuilder(rules, Tree).create_callback(None)

    if not match:

        def match_func(terminal: Terminal, node: Node) -> bool:
            return terminal.name == to_name(node)

        match = match_func

    return Parser(ParserConf(rules, callbacks, [start_symbol]), match)
