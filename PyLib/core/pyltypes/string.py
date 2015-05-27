from tokens.function import Builtin

export = {
    "string?": Builtin("string", lambda x: isinstance(x, str)), 
    "uppercase": Builtin("uppercase", lambda x: x.toupper()),
    "lowercase": Builtin("lowercase", lambda x: x.tolower()),
    "split": Builtin("split", lambda x: [y for y in x.split()])
}
