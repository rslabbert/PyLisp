import tokens
from functools import partial
import types

# Functions dealing with types, including things such as testing for types, or type conversions
# Testing for types is in here instead of inside conditionals to keep common elements connected
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
booleans = {
    "boolean?": lambda x: isinstance(x, bool),
}

symbols = {
    "symbol?": lambda x: isinstance(x, tokens.symbol.Symbol),
}

numbers = {
    "number?": lambda x: isinstance(x, (int, float)),
}

functions = {
    "procedure?": lambda x: isinstance(x, (tokens.function.Function, partial, types.BuiltinFunctionType, types.LambdaType)),
}

strings = {
    "string?": lambda x: isinstance(x, str),
}

generic = {
    "null?": lambda x: x is None,
}

lists = {
    # Car and cdr for compatibility with other schemes
    "list?": lambda x: isinstance(x, tokens.lst.Lst),
    "car": lambda x: x[0],
    "cdr": lambda x: x[1:],
    "head": lambda x: x[0],
    "tail": lambda x: x[1:],
    "init": lambda x: x[:-1],
    "last": lambda x: x[-1],
    "length": lambda x: len(x),
    "append": lambda x, y: x + y if isinstance(y, tokens.lst.Lst) else x + [y],
    "reverse": lambda x: x.reverse(),
    "take": lambda x, y: y[:x],
    "index": lambda x, y: y.index(x),
    "elem?": lambda x, y: x in y,
    "zip": lambda x, y: tokens.lst.Lst(*zip(x, y))
}

pylTypes = {}
pylTypes.update(booleans)
pylTypes.update(symbols)
pylTypes.update(numbers)
pylTypes.update(functions)
pylTypes.update(strings)
pylTypes.update(generic)
pylTypes.update(lists)
