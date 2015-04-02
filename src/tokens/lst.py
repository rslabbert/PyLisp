from tokens.token import Token


class ListStart(Token):
    """Docstring for Lst. """
    def __init__(self):
        Token.__init__(self)


class ListEnd(Token):
    """Docstring for Lst. """
    def __init__(self):
        Token.__init__(self)


class Lst(Token, list):
    def __init__(self, *secList):
        Token.__init__(self)
        list.__init__(self)
        self.extend(secList)

    def head(self):
        return self[0]

    def tail(self):
        return self[1:]

    def __getitem__(self, item):
            result = list.__getitem__(self, item)
            try:
                if isinstance(result, list) and not isinstance(result, Lst):
                    return Lst(*result)
                else:
                    return result
            except TypeError:
                return result
