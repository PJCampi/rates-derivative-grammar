from collections import deque, defaultdict
from itertools import chain
from operator import attrgetter
from typing import Iterable, Optional, List, Callable, Dict, Set

from orderedset import OrderedSet
from lark.grammar import Rule, Symbol, Terminal, NonTerminal

from .utils import classify, is_discarded_terminal, is_inline_rule


__all__ = ['Grammar']


def make_visited_predicate() -> Callable[[Rule], bool]:
    visited: Set[Rule] = set()

    def predicate(item: Rule) -> bool:
        if item not in visited:
            visited.add(item)
            return True
        return False

    return predicate


class Grammar:
    """
    contains utility functions to analyse a grammar
    """

    def __init__(self, rules: Iterable[Rule]):
        self.rules = list(rules)
        self.rules_by_origin = self.get_rules_by_origin(self.rules)

    @staticmethod
    def discard_terminals(rule: Rule) -> Rule:
        return Rule(rule.origin, [exp for exp in rule.expansion if not is_discarded_terminal(exp)],
                    rule.order, rule.alias, rule.options)

    @staticmethod
    def get_all_terminals(rules: Iterable[Rule]) -> Iterable[Symbol]:
        for rule in rules:
            yield rule.origin
            for exp in rule.expansion:
                if exp.is_term:
                    yield exp

    @staticmethod
    def get_rules_by_origin(rules: Iterable[Rule]) -> Dict[NonTerminal, List[Rule]]:
        return classify(rules, attrgetter('origin'))

    @staticmethod
    def get_parents_by_origin(rules: Iterable[Rule]) -> Dict[NonTerminal, OrderedSet]:
        by_parent: Dict[NonTerminal, OrderedSet] = defaultdict(OrderedSet)
        for rule in rules:
            for exp in rule.expansion:
                if not exp.is_term:
                    by_parent[exp].add(rule.origin)
        return by_parent

    @property
    def start(self) -> NonTerminal:
        return self.rules[0].origin

    def expand_inline_rules(self) -> Iterable[Rule]:

        rules_by_origin = self.get_rules_by_origin(reversed(self.rules))
        parents_by_origin = self.get_parents_by_origin(self.rules)

        for origin in list(rules_by_origin):
            should_expand = set(map(is_inline_rule, rules_by_origin[origin]))
            if not should_expand:
                raise ValueError(f'Inconsistent set of inline rules for origin: {origin.name}.')

            if should_expand.pop():
                rules = rules_by_origin.pop(origin)
                for parent in parents_by_origin.get(origin, []):
                    new_parent_rules = []

                    for parent_rule in rules_by_origin[parent]:
                        if origin in parent_rule.expansion:
                            for rule in rules:
                                children: List[Symbol] = []
                                for child in parent_rule.expansion:
                                    if rule.origin == child:
                                        children.extend(rule.expansion)
                                    else:
                                        children.append(child)
                                new_parent_rules.append(Rule(parent_rule.origin, children, parent_rule.order,
                                                             parent_rule.alias, parent_rule.options))
                        else:
                            new_parent_rules.append(parent_rule)
                    rules_by_origin[parent] = new_parent_rules

        yield from chain.from_iterable(reversed(list(rules_by_origin.values())))

    def get_rules(self, start: str) -> Iterable[Rule]:
        """
        gets all rules from start by breadth
        Args:
            start: the starting point in the grammar

        Returns: the list of rules

        """
        yield from self._iter_breadth_first(start, predicate=make_visited_predicate())

    def sort(self, terminal_names: Iterable[str]) -> List[str]:
        """
        sorts terminal names in order of their first appearance in the grammar (depth first)

        For example:

        a -> b
         |
         -> c
         |
         -> d -> e

         would sort [c,b,e] into [b,c,e]

        Args:
            terminal_names: the unordered list of terminal names

        Returns: the sorted list of terminal names

        """
        terminals = self.get_all_terminals(self._iter_depth_first(predicate=make_visited_predicate()))
        sorted_symbols = list(map(attrgetter('name'), terminals))
        return sorted(terminal_names, key=sorted_symbols.index)

    def trim(self, node_names: Iterable[str]) -> Iterable[Rule]:
        """
        Trim the branches of a tree at the nodes specified:

        a -> b -> c
          |
          -> d

        is trimmed to:

        a -> b
          |
          -> d

        if [c] is passed

        Args:
            node_names: list of nodes to trim the tree at

        Returns:
            the trimmed tree

        """

        node_names = set(node_names)
        if self.start.name in node_names:
            raise ValueError(f"start node: {self.start} cannot be trimmed.")

        visited: Set[Rule] = set()

        def predicate(item):
            if item.origin.name in node_names:
                return False
            return item not in visited and not visited.add(item)

        for rule in self._iter_breadth_first(predicate=predicate):

            # create new children
            children: List[Symbol] = []
            for exp in rule.expansion:
                if not exp.is_term and exp.name in node_names:
                    children.append(Terminal(exp.name))
                else:
                    children.append(exp)

            yield Rule(rule.origin, children, rule.order, rule.alias, rule.options)

    def _iter_breadth_first(self, start: Optional[str] = None, *,
                            predicate: Callable[[Rule], bool] = lambda r: True) -> Iterable[Rule]:

        start = NonTerminal(start) if start else self.start

        to_visit = deque(self.rules_by_origin[start])
        while to_visit:
            rule = to_visit.popleft()

            if predicate(rule):
                yield rule
                for next_rule in self._traverse_rule(rule):
                    to_visit.append(next_rule)

    def _iter_depth_first(self, start: Optional[str] = None, *,
                          predicate: Callable[[Rule], bool] = lambda r: True) -> Iterable[Rule]:
        def _iter(rule):
            if predicate(rule):
                yield rule
                for next_rule in self._traverse_rule(rule):
                    yield from _iter(next_rule)

        start = NonTerminal(start) if start else self.start
        for to_visit in self.rules_by_origin[start]:
            yield from _iter(to_visit)

    def _traverse_rule(self, rule: Rule) -> Iterable[Rule]:
        for exp in rule.expansion:
            if not exp.is_term:
                yield from self.rules_by_origin[exp]
