from typing import Callable

from lark import Tree, Transformer, Token

from .conversion import TokenConverterRegistry, TokenConverterRegistrationError


__all__ = ['RenameNodeTransformer', 'FromTokenConversionTransformer']


class RenameNodeTransformer(Transformer):
    """
    renames the nodes of the tree according to rename_func
    """

    def __init__(self, rename_func: Callable[[str], str]):
        self.rename_func = rename_func

    def __default__(self, data, children, meta):
        for child in children:
            if isinstance(child, Token):
                child.type = self.rename_func(child.type)
            elif isinstance(child, Tree):
                child.data = self.rename_func(child.data)
        return Tree(data, children, meta)


class FromTokenConversionTransformer(Transformer):
    """
    converts the node values according to the converter registered. Value remains unchanged if no converter is
    registered for the node.
    """

    def __default__(self, data, children, meta):
        for i, child in enumerate(children):
            if isinstance(child, Token):
                try:
                    children[i] = Token(child.type, TokenConverterRegistry.get(child.type).from_token(child))
                except TokenConverterRegistrationError:
                    pass

        return Tree(data, children, meta)
