from tokens.function import Builtin

export = {"boolean?": Builtin("boolean?", lambda x: isinstance(x, bool)), }
