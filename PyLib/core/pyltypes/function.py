import tokens
from tokens.function import Builtin

export = {
    "procedure?": Builtin("procedure?", lambda x: isinstance(x, (tokens.function.Function, partial,
                                           types.BuiltinFunctionType,
                                           types.LambdaType))),
}
