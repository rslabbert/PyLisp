from core import libs


class Env(dict):
    """The environment which is used to find variables and symbols and their associated value"""
    def __init__(self, secEnv={}):
        """secEnv variable to allow an environment to inherit from a previous one"""
        dict.__init__(self)
        self.update(secEnv)

    def setToStandardEnv(self):
        """Sets the standard environment which contains all the default and language specific symbols"""
        self.includeStandardLib("arithmetic")
        self.includeStandardLib("condition")

    def includeStandardLib(self, lib):
        val = libs.libs[lib]
        if val is not None:
            self.update(val)
        else:
            return False

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
                return False
