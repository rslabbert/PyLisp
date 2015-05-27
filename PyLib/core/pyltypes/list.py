import tokens
from tokens.function import Builtin

export = {
    "list": Builtin("list", lambda *x: [y for y in x]),
    "list?": Builtin("list?", lambda x: isinstance(x, list)),
    "car": Builtin("car", lambda x: x[0]),
    "cdr": Builtin("cdr", lambda x: x[1:]),
    "init": Builtin("init", lambda x: x[:-1]),
    "last": Builtin("last", lambda x: x[-1]),
    "length": Builtin("length", lambda x: len(x)),
    "append": Builtin("append", lambda x, y: x + y if isinstance(y, list) else x + [y]),
    "reverse": Builtin("reverse", lambda x: x.reverse()),
    "index": Builtin("index", lambda x, y: y.index(x)),
    "elem?": Builtin("elem?", lambda x, y: x in y),
    "null?": Builtin("null?", lambda x: len(x) == 0),
    "cons": Builtin("cons", lambda x, y: (x if isinstance(x, list) else [x]) + (y if isinstance(y, list) else [y]))
}
