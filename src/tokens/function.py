from tokens.token import Token
from tokens.lst import Lst


class Function(Token):
    """
    Represents a user created function
    Contains arguments, and expr, and an environment
    """

    def __init__(self, name, args, expr, env):
        Token.__init__(self)
        self.value = name
        self.args = Lst(*map(lambda x: x.value, args))
        self.expr = expr
        self.env = env

    def getEnv(self, *args):
        """
        Gets the environment by combining the provided arguments with the functions arguments
        """
        self.env.update(zip(self.args, args))
        return self.env

    def __repr__(self):
        return "{name} {args}: {expr}".format(name=self.value, args=self.args, expr=self.expr)
