import tokens
from tokens.lst import Lst
from tokens.function import Builtin

export = {
    "list": Builtin("list", lambda *x: Lst(*x)),
    "list?": Builtin("list?", lambda x: isinstance(x, Lst)),
    "car": Builtin("car", lambda x: x[0]),
    "cdr": Builtin("cdr", lambda x: x[1:]),
    "init": Builtin("init", lambda x: x[:-1]),
    "last": Builtin("last", lambda x: x[-1]),
    "length": Builtin("length", lambda x: len(x)),
    "append": Builtin("append", lambda x, y: x + y if isinstance(y, Lst) else x + Lst(y)),
    "reverse": Builtin("reverse", lambda x: x.reverse()),
    "index": Builtin("index", lambda x, y: y.index(x)),
    "elem?": Builtin("elem?", lambda x, y: x in y),
    "null?": Builtin("null?", lambda x: len(x) == 0),
    "cons": Builtin("cons", lambda x, y: (x if isinstance(x, Lst) else Lst(x)) + (y if isinstance(y, Lst) else Lst(y)))
}
