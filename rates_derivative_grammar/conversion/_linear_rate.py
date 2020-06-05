from ._generic import BooleanConverter

__all__ = ["IsImmConverter", "IsMtmConverter"]


class IsImmConverter(BooleanConverter):
    grammar = "fra"
    name = "IS_IMM"
    flag = "I"


class IsMtmConverter(BooleanConverter):
    grammar = "currency_basis_swap"
    name = "IS_MTM"
    flag = "MTM"
