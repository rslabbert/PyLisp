import tokens
from functools import partial
import types

pylTypes = {
    "boolean?": lambda x: isinstance(x, bool),
    "symbol?": lambda x: isinstance(x, tokens.symbol.Symbol),
    "null?": lambda x: x is None,
    "number?": lambda x: isinstance(x, (int, float)),
    "procedure?": lambda x: isinstance(x, (tokens.function.Function, partial, types.BuiltinFunctionType, types.LambdaType)),
    "string?": lambda x: isinstance(x, str)
}
