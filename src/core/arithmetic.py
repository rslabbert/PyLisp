import operator as op

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
}
