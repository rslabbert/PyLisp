from tokens.token import Token


class LiteralStart():
    def __init__(self):
        pass


class LiteralEnd():
    def __init__(self):
        pass


class Literal(Token):
    """Docstring for Literal. """
    def __init__(self, value):
        Token.__init__(self, value)
