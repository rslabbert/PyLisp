from errors.pylisperror import PylispError


class PylispSyntaxError(PylispError):
    """
    Used for syntax errors in pylisp, i.e. unequal amounts of opening and closing brackets
    """

    def __init__(self, expr, msg):
        PylispError.__init__(self, expr, msg)

    def __str__(self):
        return "Syntax error in expression " + repr(self.expr) + ": " + self.msg
