from errors.pylisperror import PylispError
import tokens


class PylispTypeError(PylispError):
    """
    """

    def __init__(self, expr, *args, msg=""):
        PylispError.__init__(self, expr, msg)
        self.args = map(lambda x: str(x) + ": " + str(type(x).__name__), args)

    def __str__(self):
        return "Type Error: Can't apply expression " + str(self.expr) + " to " + str(self.args) + self.msg
