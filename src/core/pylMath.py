from tokens.function import Builtin

# A math library, containing standard math functions. Can be imported into the env using import math
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
pyl_math = {
    "round": Builtin("round", lambda x: round(x)),
    "sum": Builtin("sum", lambda x: sum(x)),
}
