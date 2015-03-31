from tokens.token import Token


class Function(Token):
    """Docstring for func. """
    def __init__(self, args, expr, env):
        Token.__init__(self)
        self.value = None
        self.args = list(map(lambda x: x.value, args))
        self.expr = expr
        self.env = env

    def getEnv(self, penv, *args):
        self.env.update(penv)
        self.env.update(zip(self.args, args))
        return self.env
