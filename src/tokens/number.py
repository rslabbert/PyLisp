from tokens.token import Token


class Number(Token):
    """Docstring for Number. """
    def __init__(self, value):
        try:
            value = int(value)
        except ValueError:
            value = float(value)
        Token.__init__(self, value)
