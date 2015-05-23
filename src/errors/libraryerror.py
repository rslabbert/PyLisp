from errors.pylisperror import PylispError


class LibraryError(PylispError):
    """
    An error used when an import statement gives a library with errors
    """

    def __init__(self, expr, library, msg=""):
        PylispError.__init__(self, expr, msg)
        self.library = library

    def __str__(self):
        return "Error in library '" + str(self.library) + "', in file: '" + str(self.expr) + "':\n" + str(self.msg)
