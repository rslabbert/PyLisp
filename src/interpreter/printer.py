from tokens.function import Function


def PRINT(inp):
    """Responsible for printing the eval of the user's input"""
    if inp is None:
        return
    if isinstance(inp, Function):
        return
    else:
        print(inp)
