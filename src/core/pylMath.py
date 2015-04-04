import math

# A math library, containing standard math functions. Can be imported into the env using import math
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
pylMath = {
    "max": lambda x, y: max(x, y),
    "min": lambda x, y: min(x, y),
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
    "round": lambda x: round(x),
    "sum": lambda x: sum(x),
}
