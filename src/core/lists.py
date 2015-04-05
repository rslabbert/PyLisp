from tokens.lst.Lst import Lst

lists = {
    # Car and cdr for compatibility with other schemes
    "car": lambda x: x[0],
    "cdr": lambda x: x[1:],
    "head": lambda x: x[0],
    "tail": lambda x: x[1:],
    "init": lambda x: x[:-1],
    "last": lambda x: x[-1],
    "length": lambda x: len(x),
    "append": lambda x, y: x + y,
    "reverse": lambda x: x.reverse(),
    "take": lambda x, y: y[:x],
    "index": lambda x, y: y.index(x),
    "elem?": lambda x, y: not y.index(x) == -1,
    "zip": lambda x, y: Lst(*zip(x, y))
}
