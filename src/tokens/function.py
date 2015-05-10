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

    def get_env(self, *args):
        """
        Gets the environment by combining the provided arguments with the functions arguments
        """
        self.env.update(zip(self.args, args))
        return self.env

    def __repr__(self):
        return "{name} {args}: {expr}".format(name=self.value,
                                              args=self.args,
                                              expr=self.expr)


class Builtin(Token):
    """
    A class which holds a function defined in python and is accesible to pylisp, e.g. the + function
    """

    def __init__(self, name, func, *args):
        Token.__init__(self)
        self.value = name
        self.func = func
        self.args = args
        self.arg_len = self.func.__code__.co_argcount
        self.has_unpack_args = len(self.func.__code__.co_varnames) > self.arg_len

    def __call__(self, *args):
        return self.func(*self.args + args)

    def __repr__(self):
        return "{}".format(Lst(self.value, *self.args))
