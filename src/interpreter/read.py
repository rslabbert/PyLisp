from parser import Parser


def READ(inp):
    """
    Reads the user input and parses it
    """
    parser = Parser()
    return parser.parseBuffer(inp)
