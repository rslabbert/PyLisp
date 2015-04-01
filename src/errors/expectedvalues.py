from errors.pylisperror import PylispError


class ExpectedValues(PylispError):
    """Docstring for ExpectedValues. """
    def __init__(self, expr="", msg=""):
        PylispError.__init__(self, expr, msg)

    def __str__(self):
        return "Expected values"
