import operator as op
import math

# Contains basic arithmetic which will always be included into the standard environment
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
arithmetic = {
    "+": lambda x, y: op.add(x, y),
    "-": lambda x, y: op.sub(x, y),
    "*": lambda x, y: op.mul(x, y),
    "/": lambda x, y: op.truediv(x, y),
    "expt": lambda x, y: op.pow(x, y),
    "modulo": lambda x, y: op.mod(x, y),
    "max": lambda x: max(x),
    "min": lambda x: min(x),
    "abs": lambda x: abs(x),
    "sqrt": lambda x: math.sqrt(x),
    "sin": lambda x: math.sin(x),
    "cos": lambda x: math.cos(x),
    "tan": lambda x: math.tan(x),
    "asin": lambda x: math.asin(x),
    "acos": lambda x: math.acos(x),
    "atan": lambda x: math.atan(x),
    "atan2": lambda x: math.atan2(x),
    "log": lambda x: math.log(x),
    "log10": lambda x: math.log10(x),
    "loge": lambda x: math.log1p(x),
    "floor": lambda x: math.floor(x),
    "ceil": lambda x: math.ceil(x),
    "pi": math.pi,
    "e": math.e,
}
