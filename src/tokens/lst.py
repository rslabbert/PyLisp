from tokens.token import Token


class Lst(Token, list):
    """
    Replaces the use of list in the virtual machine
    """

    def __init__(self, *args):
        """
        secList is provided to initialise the lst with values
        """
        Token.__init__(self)
        list.__init__(self, args)

    def __add__(self, x):
        return Lst(*list.__add__(self, x))

    def __getitem__(self, item):
        """
        Overides list's getitem function to make that the value returned is always a Lst or if it is a single value it returns the value
        """
        result = list.__getitem__(self, item)
        if type(result) == type(list()):
            return Lst(*result)
        else:
            return result

    def __repr__(self):
        string = ""
        for i in self:
            string += str(i) + " "
        string = "(" + string[:].strip() + ")"

        return string
