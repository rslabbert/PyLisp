from errors.pylisperror import PylispError


class SymbolNotFound(PylispError):
    """
    Error used for when a symbol is given which does not exist in the environment or is not a core keyword
    """

    def __init__(self, expr, msg=""):
        PylispError.__init__(self, expr, msg)

    def __str__(self):
        return "Could not find symbol " + self.expr
