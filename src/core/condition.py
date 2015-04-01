import operator as op

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
    "#t": True,
    "#f": False,
}
