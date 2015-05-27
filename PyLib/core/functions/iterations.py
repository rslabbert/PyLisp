from tokens.function import Builtin
import itertools

export = {
    "range": Builtin("range", lambda x, y, *z: range(x, y, z[0])
                     if z else range(x, y)),
    "take": Builtin("take", lambda x, y: [i for i in itertools.islice(y, x)]),
    "nth": Builtin("nth", lambda x, y: next(itertools.islice(y, x, None))),
    "repeat": Builtin("repeat", lambda x, *y: itertools.repeat(x, y[0])
                      if y else itertools.repeat(x)),
    "collect": Builtin("collect", lambda x: [y for y in x]),
    "count": Builtin("count", lambda x: itertools.count(x))
}
