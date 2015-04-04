from errors.pylisperror import PylispError


class LibraryNotFound(PylispError):

    """
    An error used when an import statement gives a library which does not exist
    """

    def __init__(self, expr, msg=""):
        PylispError.__init__(self, expr, msg)

    def __str__(self):
        return "Could not find library " + self.expr
