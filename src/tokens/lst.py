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
    def __init__(self):
        Token.__init__(self)
        list.__init__(self)
