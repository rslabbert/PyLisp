from functools import partial
import operator as op

import tokens


class Env(dict):
    """The environment which is used to find variables and symbols and their associated value"""
    def __init__(self, secEnv={}):
        """secEnv variable to allow an environment to inherit from a previous one"""
        dict.__init__(self)
        self.update(secEnv)

    def setToStandardEnv(self):
        """Sets the standard environment which contains all the default and language specific symbols"""
        self.update({
            "+": op.add,
            "-": op.sub,
            "*": op.mul,
            "/": op.truediv,
            "=": op.eq,
            ">": op.gt,
            "<": op.lt,
            ">=": op.ge,
            "<=": op.le,
            "max": max,
            "min": min,
            "abs": abs,
            "modulo": op.mod,
            "not": op.not_,
            "and": op.and_,
            "or": op.or_,
            "nil": None,
            "boolean?": lambda x: True if x is True else False,
            "symbol?": lambda x: True if isinstance(x, tokens.symbol.Symbol) else False,
            "#t": True,
            "#f": False,
            "newline": partial(print, ""),
            "display": partial(print, end="")})

    def set(self, keys, vals):
        """Convenience function for self.update with a single value which returns the value inserted"""
        if isinstance(keys, list):
            for i, k in enumerate(keys):
                self.update({k: vals[i]})
            return
        else:
            self.update({keys: vals})
            return vals

    def get(self, key, default=None):
        """Convenience function for self[key] which return the value if found, else raises an error which tells the user the symbol was not found"""
        try:
            return self[key]
        except:
            if default:
                return default
            else:
                return None
