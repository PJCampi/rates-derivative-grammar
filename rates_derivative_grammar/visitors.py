from typing import Dict, Any, Iterable

from lark import Visitor, Tree, Token

from .utils import Node, to_name, to_value, normalize


__all__ = ["AttributeVisitor", "get_tokens_dict"]


class AttributeVisitor(Visitor):
    """
    Extract the nodes specified in __init__ from the parsed tree.
    """

    def __init__(self, node_names: Iterable[str]):

        self.tokens: Dict[str, Token] = {}
        self.node_names = set(node_names)

    def __call__(self, tree: Tree) -> Dict[str, Any]:
        self.visit(tree)
        return self.tokens

    def __default__(self, tree: Tree) -> None:
        for child in tree.children:
            name = to_name(child)
            if name in self.node_names:
                self.tokens[name] = to_value(child)


def get_tokens_dict(node: Node) -> Dict[str, Any]:
    """

    Args:
        node: the starting node

    Returns: a nested dictionary of str to Any representing the tree

    """

    # iterate over the function
    key = normalize(to_name(node))
    if isinstance(node, Tree):

        # if one defines a rule that is only just representing a token
        if len(node.children) == 1 and normalize(to_name(node.children[0])) == key:
            return get_tokens_dict(node.children[0])

        return {key: {k: v for child in node.children for k, v in get_tokens_dict(child).items()}}

    # if it is only a token
    return {key: to_value(node)}
