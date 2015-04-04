class PylispError(Exception):

    """
    A parent error for every error which stems from pylisp itself. This enables filtering between errors which should be fed to the user or errors which stem from python
    """

    def __init__(self, expr, msg):
        Exception.__init__(self)
        self.expr = expr
        self.msg = msg

    def __str__(self):
        return "Error in " + repr(self.expr) + ": " + repr(self.msg)
