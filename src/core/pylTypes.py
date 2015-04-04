import tokens
from functools import partial
import types

# Functions dealing with types, including things such as testing for types, or type conversions
# Testing for types is in here instead of inside conditionals to keep common elements connected
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
pylTypes = {
    "boolean?": lambda x: isinstance(x, bool),
    "symbol?": lambda x: isinstance(x, tokens.symbol.Symbol),
    "null?": lambda x: x is None,
    "number?": lambda x: isinstance(x, (int, float)),
    "procedure?": lambda x: isinstance(x, (tokens.function.Function, partial, types.BuiltinFunctionType, types.LambdaType)),
    "string?": lambda x: isinstance(x, str),
    "list?": lambda x: isinstance(x, tokens.lst.Lst)
}
