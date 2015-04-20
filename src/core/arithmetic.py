import operator as op
import math
from tokens.function import Builtin

# Contains basic arithmetic which will always be included into the standard environment
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
arithmetic = {
    "+": Builtin("+", lambda x, y: op.add(x, y)),
    "-": Builtin("-", lambda x, y: op.sub(x, y)),
    "*": Builtin("*", lambda x, y: op.mul(x, y)),
    "/": Builtin("/", lambda x, y: op.truediv(x, y)),
    "expt": Builtin("expt", lambda x, y: op.pow(x, y)),
    "modulo": Builtin("modulo", lambda x, y: op.mod(x, y)),
    "max": Builtin("max", lambda x: max(x)),
    "min": Builtin("min", lambda x: min(x)),
    "abs": Builtin("abs", lambda x: abs(x)),
    "sqrt": Builtin("sqrt", lambda x: math.sqrt(x)),
    "sin": Builtin("sin", lambda x: math.sin(x)),
    "cos": Builtin("cos", lambda x: math.cos(x)),
    "tan": Builtin("tan", lambda x: math.tan(x)),
    "asin": Builtin("asin", lambda x: math.asin(x)),
    "acos": Builtin("acos", lambda x: math.acos(x)),
    "atan": Builtin("atan", lambda x: math.atan(x)),
    "atan2": Builtin("atan2", lambda x: math.atan2(x)),
    "log": Builtin("log", lambda x: math.log(x)),
    "log10": Builtin("log10", lambda x: math.log10(x)),
    "loge": Builtin("loge", lambda x: math.log1p(x)),
    "floor": Builtin("floor", lambda x: math.floor(x)),
    "ceil": Builtin("ceil", lambda x: math.ceil(x)),
    "pi": math.pi,
    "e": math.e,
}
