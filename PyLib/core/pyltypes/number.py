from tokens.function import Builtin

export = {"number?": Builtin("number?", lambda x: isinstance(x, (int, float))), }
