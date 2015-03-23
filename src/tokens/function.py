from env import Env
from tokens.token import Token


class Function(Token):
    """Docstring for func. """
    def __init__(self, args, expr, env):
        Token.__init__(self)
        self.args = list(map(lambda x: x.value, args))
        self.expr = expr
        self.env = env

    def getEnv(self, penv, *args):
        env = Env(penv)
        env.update(zip(self.args, args))
        return env

    def __call__(self, *args):
        return self.expr, self.getEnv(self.env, *args)
