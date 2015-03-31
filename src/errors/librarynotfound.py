from errors.pylisperror import PylispError


class LibraryNotFound(PylispError):
    """Docstring for LibraryNotFound. """
    def __init__(self, expr, msg=""):
        PylispError.__init__(self, expr, msg)

    def __str__(self):
        return "Could not find library " + self.expr
