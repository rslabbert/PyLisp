from tokens.token import Token


class Literal(Token):
    """
    Represents a literal, where everything is given as is, e.g. 'test -> test '1 -> 1 '(1 2 3) -> (1 2 3)
    """

    def __init__(self, value):
        Token.__init__(self, value)

    def __repr__(self):
        return self.value
