import operator as op
from tokens.pylsyntax import PylSyntax
from tokens.function import Builtin

# Containes conditional keywords, these are always included in the standard environment
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
condition = {
    "=": Builtin("=", lambda x, y: op.eq(x, y)),
    ">": Builtin(">", lambda x, y: op.gt(x, y)),
    "<": Builtin("<", lambda x, y: op.lt(x, y)),
    ">=": Builtin(">=", lambda x, y: op.ge(x, y)),
    "<=": Builtin("<=", lambda x, y: op.le(x, y)),
    "not": Builtin("not", lambda x: op.not_(x)),
    "and": Builtin("and", lambda x, y: op.and_(x, y)),
    "or": Builtin("or", lambda x, y: op.or_(x, y)),
    "nil": None,
    "#t": True,
    "#f": False,
    "else": PylSyntax.sElse,  # Used for cond
}
