from errors.pylisperror import PylispError


class PylispSyntaxError(PylispError):
    """Docstring for SyntaxError. """
    def __init__(self, expr, msg):
        PylispError.__init__(self, expr, msg)

    def __str__(self):
        return "Syntax error in expression " + repr(self.expr) + ": " + self.msg
