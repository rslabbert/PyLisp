from errors.pylisperror import PylispError


class FileNotFoundError(PylispError):
    def __init__(self, expr, msg=""):
        PylispError.__init__(self, expr, msg)

    def __str__(self):
        return "Could not find file " + self.expr
