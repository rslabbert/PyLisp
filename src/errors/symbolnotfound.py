from errors.pylisperror import PylispError


class SymbolNotFound(PylispError):
    """Docstring for SymbolNotFound. """
    def __init__(self, msg, info=""):
        PylispError.__init__(self, msg, info)

    def __str__(self):
        return "Could not find symbol " + self.msg
