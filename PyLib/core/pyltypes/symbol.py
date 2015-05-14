import tokens
from tokens.function import Builtin

export = {"symbol?": Builtin("symbol?", lambda x: isinstance(x, tokens.symbol.Symbol)), }
