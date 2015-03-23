from lexer import Lexer


def READ(inp):
    """Reads the user input and parses it using a lexer"""
    lexer = Lexer()
    return lexer.parseBuffer(inp)
