# A math library, containing standard math functions. Can be imported into the env using import math
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
pylMath = {
    "round": lambda x: round(x),
    "sum": lambda x: sum(x),
}
