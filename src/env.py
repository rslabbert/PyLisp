class Env(dict):
    """The environment which is used to find variables and symbols and their associated value"""
    def __init__(self, secEnv={}):
        """secEnv variable to allow an environment to inherit from a previous one"""
        dict.__init__(self)
        self.update(secEnv)

    def setToStandardEnv(self):
        """Sets the standard environment which contains all the default and language specific symbols"""
        import operator as op
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
            "not": op.not_,
            "and": op.and_,
            "or": op.or_,
            "#t": True,
            "#f": False})

    def set(self, key, val):
        """Convenience function for self.update with a single value which returns the value inserted"""
        self.update({key: val})
        return val

    def get(self, key):
        """Convenience function for self[key] which return the value if found, else raises an error which tells the user the symbol was not found"""
        try:
            return self[key]
        except:
            print("Symbol", key, "not found")
