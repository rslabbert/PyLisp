import operator as op
import tokens

condition = {
    "=": op.eq,
    ">": op.gt,
    "<": op.lt,
    ">=": op.ge,
    "<=": op.le,
    "not": op.not_,
    "and": op.and_,
    "or": op.or_,
    "nil": None,
    "boolean?": lambda x: True if x is True else False,
    "symbol?": lambda x: True if isinstance(x, tokens.symbol.Symbol) else False,
    "#t": True,
    "#f": False,
}
