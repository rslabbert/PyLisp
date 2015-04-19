import operator as op
from tokens.pylsyntax import PylSyntax

# Containes conditional keywords, these are always included in the standard environment
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
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
