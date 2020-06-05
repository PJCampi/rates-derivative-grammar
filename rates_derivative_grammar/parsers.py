from functools import partial
from glob import glob
from functools import lru_cache
import os
import re
from typing import Optional, Dict, Any, Tuple, Iterable, List

from lark import Lark, Token, Tree
from lark.grammar import NonTerminal, Terminal
from lark.lexer import TerminalDef
from lark.load_grammar import EXT, IMPORT_PATHS
from lark.reconstruct import Reconstructor

from .conversion import TokenConverterRegistry, TokenConversionError, TokenConverterRegistrationError
from .grammar_analysis import Grammar
from .processing import processors_registry, to_processor_key
from .transformers import RenameNodeTransformer, FromTokenConversionTransformer
from .utils import to_path_root, normalize, PATH_DELIMITER, make_parser, to_name, denormalize, Node
from .visitors import AttributeVisitor

__all__ = ["AssetClassParser", "AssetClassFormatter", "GRAMMAR_PATH"]

GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "grammar")
if GRAMMAR_PATH not in IMPORT_PATHS:
    IMPORT_PATHS.append(GRAMMAR_PATH)

UNKNOWN = "UNKNOWN"


class AssetClassParser:
    """ The parser parses strings """

    def __init__(self, asset_class: str, *, grammar_path: Optional[str] = None):

        self.asset_class = asset_class
        self.grammar_path = grammar_path or GRAMMAR_PATH
        self.parser = self._make_parser(self.grammar_path, self.asset_class)

    def parse(self, string: str) -> Tuple[str, Dict[str, Any]]:
        """
        parses the string specified according to the grammar defined in the Parser
        Args:
            string: the string to parse

        Returns: A tuple of the type of product parsed and a dict of the attribute parsed as
        {attribute_name: attribute value}

        """

        # parse string
        parsed = self.parser.parse(string)

        # get product tree
        if len(parsed.children) != 1:
            # This should never happen
            raise NotImplementedError("Something is wrong with your grammar. Only one product should be parsed by it.")

        product = parsed.children[0]
        product_type = product.data

        # make transformers and transform tree
        # NOTE: I am using lark's Transformer class to apply transformations to the tree in place while resolving (for
        # example converting the tokens retrieved to desired types) in place while resolving.
        # It is more efficient than parsing first and transforming afterwards.

        # converts a node value with the converter registered for the node
        token_converter = FromTokenConversionTransformer()

        # convert from node name in the grammar to attribute name (take token name only instead of full path & normalize
        # terminal names from upper case to lower case.
        node_renamer = RenameNodeTransformer(lambda s: normalize(to_path_root(s)))

        # reduces the tree nodes when relevant (see processor documentation for more info)
        processor = processors_registry[to_processor_key(self.asset_class, product_type)]()

        transformed = (token_converter * node_renamer * processor).transform(product)

        # visit tree and return attributes dict
        visitor = AttributeVisitor(processor.attribute_names)
        attributes_dict = visitor(transformed)

        # return result
        return product_type, attributes_dict

    @lru_cache(maxsize=32)
    def _make_parser(self, grammar_path: str, asset_class: str) -> Lark:
        """
        instantiate an instance of the grammar parser
        """
        grammar, products = [], []
        for file_path in glob(os.path.join(grammar_path, f"{asset_class}*{EXT}")):
            to_import = os.path.basename(file_path).replace(EXT, "")
            product = to_path_root(to_import)
            grammar.append(f"%import .{to_import}.start -> {product}")
            products.append(product)

        grammar.append(f"start: {' | '.join(products)}")
        return Lark("\n".join(grammar))


class TokenMatcher:
    def __init__(self, terminals: Iterable[TerminalDef]):
        self.terminals_dict = {Terminal(def_.name): re.compile(def_.pattern.to_regexp()) for def_ in terminals}

    def match(self, terminal: Terminal, token: Token) -> bool:
        """

        Args:
            terminal: the terminal to match
            token: the token to match against the terminal

        Returns: a match if the token's string value parses into the terminal
        """

        if token.type != UNKNOWN:
            if token.type not in terminal.name:
                return False

        try:
            converter = TokenConverterRegistry.get(terminal.name)
            value = converter.to_token(terminal.name, token.value)
        except (TokenConverterRegistrationError, TokenConversionError):
            if isinstance(token.value, str):
                value = token.value
            else:
                return False

        pattern = self.terminals_dict[terminal]
        return bool(pattern.match(value))


class AssetClassFormatter:
    """ The formatter formats attributes """

    def __init__(self, asset_class: str, *, grammar_path: Optional[str] = None):
        self.asset_class = asset_class
        self.grammar_path = grammar_path or GRAMMAR_PATH

    @staticmethod
    def _make_converted_tree(rule, children):
        """

        Args:
            rule:
            children: the children nodes of

        Returns: A tree where the children are converted

        """
        for i, (symbol, child) in enumerate(zip(rule.expansion, children)):
            if symbol.is_term:
                try:
                    children[i] = TokenConverterRegistry.get(symbol.name).to_token(symbol.name, child.value)
                except TokenConverterRegistrationError:
                    children[i] = Token(symbol.name, child.value)
        return Tree(rule.origin.name, children)

    @staticmethod
    def _make_attributes_nodes(attributes_dict: Dict[str, Any], rule_names: Iterable[NonTerminal]) -> List[Node]:
        """

        Args:
            attributes_dict: attributes to format
            rule_names: the rules that make up the grammar to format

        Returns: the nodes representing the attributes

        """
        rule_names, nodes = set(rule_names), []
        for name, val in attributes_dict.items():
            if NonTerminal(name) in rule_names:
                children = val if isinstance(val, (list, tuple)) else [val]
                nodes.append(Tree(name, list(map(partial(Token, UNKNOWN), children))))
            else:
                nodes.append(Token(denormalize(name), val))
        return nodes

    def format(self, product_type: str, attributes_dict: Dict[str, Any]):
        """
        formats attribute dictionary into a grammar string according to the grammar defined in the Formatter

        some attributes (f.ex. start_time/end_time) are non-terminal nodes of the grammar, which means that one
        cannot use Lark's reconstructor directly.
        Instead we create a parser for each sub-grammar defining the non-terminals attribute and use it to parse it
        into a sub-tree. We "piece together "these subtrees into the full parsed tree, which we then format.

        Args:
            product_type: the type of product to format
            attributes_dict: the attributes of the product to format as {attribute_name: attribute_value}

        Returns: The formatted string

        """

        # get grammar analysing tools
        grammar, analyser, reconstructor, token_matcher = self._make_grammar_tools(product_type)

        # make nodes from attribute names
        nodes = self._make_attributes_nodes(attributes_dict, analyser.rules_by_origin.keys())

        # pre-process nodes: used for example if some transformation of attributes is needed before attributes can be
        # formatted by the grammar
        processor = processors_registry[to_processor_key(self.asset_class, product_type)]
        nodes = list(processor.pre_process(nodes))

        # we create a parser for the sub-grammar that defines each non-terminal attribute nodes and recreate its
        # sub-tree
        for i, node in enumerate(nodes):
            if isinstance(node, Tree):
                rules = list(analyser.get_rules(node.data))
                token_parser = make_parser(
                    rules,
                    start_symbol=node.data,
                    match=token_matcher.match,
                    callbacks={rule: partial(self._make_converted_tree, rule) for rule in rules},
                )
                nodes[i] = token_parser.parse(node.children, start=node.data)
            else:
                nodes[i] = TokenConverterRegistry.get(node.type).to_token(node.type, node.value)

        # Trim the grammar to the nodes that have been resolved by the parsers
        trimmed_rules = analyser.trim(map(to_name, nodes))

        # NOTE: this part is actually interesting. We use the power of the parsing logic to parse the list of sub-trees
        # according to the grammar (instead of a string i.e. list of characters).
        # The match criteria used is the name of the node. This allows us to finalize the reconstruction of the tree
        # used to parse the
        parser = make_parser(trimmed_rules, match=lambda term, nod: to_name(nod) == term.name)
        tree = parser.parse(nodes, start="start")

        # reconstruct
        # NOTE: for some reason reconstructor.reconstruct appends a space between all alphanumerical characters so
        # I had to use ._reconstruct instead.
        string = "".join(reconstructor._reconstruct(tree))

        return string

    @lru_cache(maxsize=32)
    def _make_grammar_tools(self, product_type: str) -> Tuple[Lark, Grammar, Reconstructor, TokenMatcher]:
        """
        instantiate an instance of the grammar parser, the "Grammar" analyser tool, and the reconstructor
        """
        # get grammar analyser
        path = os.path.join(self.grammar_path, f"{self.asset_class}{PATH_DELIMITER}{product_type}{EXT}")
        grammar = Lark.open(path)

        # make analyser
        analyser = Grammar(grammar.rules)
        expanded_rules = map(analyser.discard_terminals, analyser.expand_inline_rules())
        analyser = Grammar(expanded_rules)

        # make reconstructor
        reconstructor = Reconstructor(grammar)

        # make token matcher
        token_matcher = TokenMatcher(grammar.terminals)

        return grammar, analyser, reconstructor, token_matcher
