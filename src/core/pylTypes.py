import tokens
from tokens.function import Builtin
from functools import partial
import types

# Functions dealing with types, including things such as testing for types, or type conversions
# Testing for types is in here instead of inside conditionals to keep common elements connected
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
booleans = {"boolean?": Builtin("boolean?", lambda x: isinstance(x, bool)), }

symbols = {"symbol?": Builtin("symbol?", lambda x: isinstance(x, tokens.symbol.Symbol)), }

numbers = {"number?": Builtin("number?", lambda x: isinstance(x, (int, float))), }

functions = {
    "procedure?": Builtin("procedure?", lambda x: isinstance(x, (tokens.function.Function, partial,
                                           types.BuiltinFunctionType,
                                           types.LambdaType))),
}

strings = {"string?": Builtin("string", lambda x: isinstance(x, str)), }

generic = {"nil?": Builtin("nil?", lambda x: x is None), }

lists = {
    "list": Builtin("list", lambda *x: tokens.lst.Lst(*x)),
    "list?": Builtin("list?", lambda x: isinstance(x, tokens.lst.Lst)),
    "car": Builtin("car", lambda x: x[0]),
    "cdr": Builtin("cdr", lambda x: x[1:]),
    "init": Builtin("init", lambda x: x[:-1]),
    "last": Builtin("last", lambda x: x[-1]),
    "length": Builtin("length", lambda x: len(x)),
    "append": Builtin("append", lambda x, y: x + y if isinstance(y, tokens.lst.Lst) else x + Lst(y)),
    "reverse": Builtin("reverse", lambda x: x.reverse()),
    "take": Builtin("take", lambda x, y: y[:x]),
    "index": Builtin("index", lambda x, y: y.index(x)),
    "elem?": Builtin("elem?", lambda x, y: x in y),
    "null?": Builtin("null?", lambda x: len(x) == 0)
}

pyl_types = {}
pyl_types.update(booleans)
pyl_types.update(symbols)
pyl_types.update(numbers)
pyl_types.update(functions)
pyl_types.update(strings)
pyl_types.update(generic)
pyl_types.update(lists)
