from tokens.token import Token


class Lst(Token, list):
    """
    Replaces the use of list in the virtual machine
    """

    def __init__(self, *sec_list):
        """
        secList is provided to initialise the lst with values
        """
        Token.__init__(self)
        list.__init__(self)
        self.extend(sec_list)

    def __add__(self, x):
        temp = Lst()
        temp.extend(self)
        temp.extend(x)
        return temp

    def __getitem__(self, item):
        """
        Overides list's getitem function to make that the value returned is always a Lst or if it is a single value it returns the value
        """
        result = list.__getitem__(self, item)
        try:
            if isinstance(result, list) and not isinstance(result, Lst):
                return Lst(*result)
            else:
                return result
        except TypeError:
            return result

    def __repr__(self):
        string = ""
        for i in self:
            string += str(i) + " "
        string = "(" + string[:].strip() + ")"

        return string
