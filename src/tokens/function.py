from tokens.token import Token


class Function(Token):
    """
    Represents a user created function
    Contains arguments, and expr, and an environment
    """

    def __init__(self, args, expr, env):
        Token.__init__(self)
        self.value = None
        self.args = list(map(lambda x: x.value, args))
        self.expr = expr
        self.env = env

    def getEnv(self, *args):
        """
        Gets the environment by combining the provided arguments with the functions arguments
        """
        self.env.update(zip(self.args, args))
        return self.env
