from tokens.function import Builtin
from tokens.lst import Lst

export = {
    "string?": Builtin("string", lambda x: isinstance(x, str)), 
    "uppercase": Builtin("uppercase", lambda x: x.toupper()),
    "lowercase": Builtin("lowercase", lambda x: x.tolower()),
    "split": Builtin("split", lambda x: Lst(*x.split()))
}
