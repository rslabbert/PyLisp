class PylispError(Exception):
    """Docstring for PylispError. """
    def __init__(self, expr, msg):
        Exception.__init__(self)
        self.expr = expr
        self.msg = msg

    def __str__(self):
        return "Error in " + repr(self.expr) + ": " + repr(self.msg)
