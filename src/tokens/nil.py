from tokens.token import Token


class Nil(Token):
    def __init__(self):
        Token.__init__(self, None)

    def __repr__(self):
        return "nil"
