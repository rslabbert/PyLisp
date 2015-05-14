from tokens.function import Builtin
from tokens.lst import Lst
import itertools

export = {
    "range": Builtin("range", lambda x, y, *z: range(x, y, z[0])
                     if z else range(x, y)),
    "take": Builtin("take", lambda x, y: Lst(*itertools.islice(y, x))),
    "nth": Builtin("nth", lambda x, y: next(itertools.islice(y, x, None))),
    "repeat": Builtin("repeat", lambda x, *y: itertools.repeat(x, y[0])
                      if y else itertools.repeat(x)),
    "collect": Builtin("collect", lambda x: Lst(*x)),
    "count": Builtin("count", lambda x: itertools.count(x))
}
