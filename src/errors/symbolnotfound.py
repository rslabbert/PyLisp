from errors.pylisperror import PylispError


class SymbolNotFound(PylispError):
    """Docstring for SymbolNotFound. """
    def __init__(self, expr, msg=""):
        PylispError.__init__(self, expr, msg)

    def __str__(self):
        return "Could not find symbol " + self.expr
