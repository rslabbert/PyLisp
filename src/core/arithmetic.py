import operator as op

arithmetic = {
    "+": lambda x, y: op.add(x, y),
    "-": lambda x, y: op.sub(x, y),
    "*": lambda x, y: op.mul(x, y),
    "/": lambda x, y: op.truediv(x, y),
    "expt": lambda x, y: op.pow(x, y),
    "modulo": lambda x, y: op.mod(x, y),
}
