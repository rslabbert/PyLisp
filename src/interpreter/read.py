from parser import Parser


def READ(inp):
    """Reads the user input and parses it using a lexer"""
    parser = Parser()
    return parser.parseBuffer(inp)
