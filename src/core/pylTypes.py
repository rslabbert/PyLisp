import tokens
from functools import partial
import types

# Functions dealing with types, including things such as testing for types, or type conversions
# Testing for types is in here instead of inside conditionals to keep common elements connected
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
booleans = {"boolean?": lambda x: isinstance(x, bool), }

symbols = {"symbol?": lambda x: isinstance(x, tokens.symbol.Symbol), }

numbers = {"number?": lambda x: isinstance(x, (int, float)), }

functions = {
    "procedure?": lambda x: isinstance(x, (tokens.function.Function, partial,
                                           types.BuiltinFunctionType,
                                           types.LambdaType)),
}

strings = {"string?": lambda x: isinstance(x, str), }

generic = {"nil?": lambda x: x is None, }

lists = {
    "list": lambda *x: tokens.lst.Lst(*x),
    "list?": lambda x: isinstance(x, tokens.lst.Lst),
    "car": lambda x: x[0],
    "cdr": lambda x: x[1:],
    "init": lambda x: x[:-1],
    "last": lambda x: x[-1],
    "length": lambda x: len(x),
    "append": lambda x, y: x + y if isinstance(y, tokens.lst.Lst) else x + [y],
    "reverse": lambda x: x.reverse(),
    "take": lambda x, y: y[:x],
    "index": lambda x, y: y.index(x),
    "elem?": lambda x, y: x in y,
    "null?": lambda x: len(x) == 0
}

pyl_types = {}
pyl_types.update(booleans)
pyl_types.update(symbols)
pyl_types.update(numbers)
pyl_types.update(functions)
pyl_types.update(strings)
pyl_types.update(generic)
pyl_types.update(lists)
