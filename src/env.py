from core import libs
from tokens.pylSyntax import PylSyntax


class Env(dict):

    """
    The environment which is used to find variables and symbols and their associated value
    """

    def __init__(self, secEnv={}):
        """
        secEnv variable to allow an environment to inherit from a previous one
        """
        dict.__init__(self)
        self.update(secEnv)

    def setToStandardEnv(self):
        """
        Sets the standard environment which contains all the default and language specific symbols
        """
        self.includeStandardLib("arithmetic")
        self.includeStandardLib("condition")
        self.includeStandardLib("types")
        env = self
        self.update({"debug": lambda: print(env)})

    def includeStandardLib(self, lib):
        """
        Searches for the provided lib in the lib lookup table, and if found inserts it into the environment otherwise returns false
        """
        val = libs.libs[lib]
        if val is not None:
            self.update(val)
        else:
            return False

    def set(self, keys, vals):
        """
        Convenience function for self.update which accepts a range of keys and values. If a single key, value is given, it is then returned after being inserted
        """
        if isinstance(keys, list):
            for i, k in enumerate(keys):
                self.update({k: vals[i]})
            return
        else:
            self.update({keys: vals})
            return vals

    def get(self, key, default=PylSyntax.sNil):
        """
        Convenience function for self[key] which return the value if found, otherwise returns default
        """
        try:
            return self[key]
        except:
            return default
