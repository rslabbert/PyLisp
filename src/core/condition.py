import operator as op
from tokens.pylSyntax import PylSyntax

condition = {
    "=": lambda x, y: op.eq(x, y),
    ">": lambda x, y: op.gt(x, y),
    "<": lambda x, y: op.lt(x, y),
    ">=": lambda x, y: op.ge(x, y),
    "<=": lambda x, y: op.le(x, y),
    "not": lambda x: op.not_(x),
    "and": lambda x, y: op.and_(x, y),
    "or": lambda x, y: op.or_(x, y),
    "nil": None,
    "#t": True,
    "#f": False,
    "else": PylSyntax.sElse,  # Used for cond
}
