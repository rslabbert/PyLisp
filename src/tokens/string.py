from tokens.token import Token


class String(Token):
    """
    Represents a string
    """

    def __init__(self, value):
        Token.__init__(self, value)

    def __repr__(self):
        return self.value
