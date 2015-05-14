from tokens.function import Builtin

export = {"nil?": Builtin("nil?", lambda x: x is None), }
