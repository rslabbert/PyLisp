from tokens.token import Token


class Number(Token):
    """
    Represents a number. The value is encoded as an int or float at initialisation
    """

    def __init__(self, value):
        try:
            value = int(value)
        except ValueError:
            value = float(value)
        Token.__init__(self, value)
