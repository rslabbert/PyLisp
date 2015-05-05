from enum import Enum

import tokens.function
import tokens.lst
import tokens.symbol
import tokens.nil
import tokens.number
import tokens.string
import tokens.literal
from errors import syntaxerror


class State(Enum):
    """
    Every type which a token can embody
    """

    nil = 0
    comment = 1
    string = 2
    symbol = 3
    num = 4
    literal = 5


class Parser:
    """
    Class responsible for parsing user input
    """

    def __init__(self):
        self.state = State.nil
        self.data = []
        self.position = 0

    @staticmethod
    def is_operator(string):
        """
        Checks if the character provided is a operator
        """
        return ["+", "-", "*", "/", "^", "%", "=", ">", "<", ">=", "<=", "?",
                "!", "-", "#", ":", ";", "$", "&", ".", "@", "_", "~", "#",
                "\\"].__contains__(string)

    def parse_token(self, buf):
        """
        Loops through a buffer and returns the first token
        """
        current_token = ""
        self.state = State.nil

        for i in range(0, len(buf)):
            self.position += 1
            c = buf[i]

            # Sets the initial State
            if self.state == State.nil:
                if c == "'":
                    return tokens.literal.LiteralStart()
                elif c == ";":
                    self.state = State.comment
                elif c == '"':
                    self.state = State.string
                elif c == "(":
                    return tokens.lst.ListStart()
                elif c == ")" or c == "]":
                    return tokens.lst.ListEnd()
                elif c == "[":
                    return [tokens.lst.ListStart(),
                            tokens.symbol.Symbol("list")]
                elif c == "." and buf[i + 1].isspace():
                    return tokens.lst.Cons()
                elif c.isalpha() or (self.is_operator(c) and not buf[i + 1].isdigit()):
                    self.state = State.symbol
                elif c.isdigit() or (c == "-" and buf[i + 1].isdigit()):
                    self.state = State.num

            # Parses a string
            elif self.state == State.string:
                if c == '"':
                    return tokens.string.String(current_token)
                elif c.isalnum() or c.isspace() or self.is_operator(c):
                    current_token += c

            # Parses a symbol or number
            if self.state == State.symbol:
                if c.isspace() or c == "\n":
                    return tokens.symbol.Symbol(current_token)
                elif c == "(" or c == ")" or c == "[" or c == "]":
                    self.position -= 1
                    return tokens.symbol.Symbol(current_token)
                else:
                    current_token += c

            elif self.state == State.num:
                if c.isspace() or c == "\n":
                    return tokens.number.Number(current_token)
                elif c == "(" or c == ")" or c == "[" or c == "]":
                    self.position -= 1
                    return tokens.number.Number(current_token)
                else:
                    current_token += c

        # Handles end of buffer strings not being closed or symbols being at
        # end
        if self.state == State.symbol:
            return tokens.symbol.Symbol(current_token)
        if self.state == State.num:
            return tokens.number.Number(current_token)

        if self.state == State.string:
            print("String not closed before newline")
            return False

    def create_syntax_tree(self, data):
        """
        Takes a parsed buffer and returns a syntax tree where parens are replaced with lists containing the items between them and literals are replaced with literals
        """
        tree = tokens.lst.Lst()
        i = 0
        while i < len(data):
            # Parses a literal
            if isinstance(data[i], tokens.literal.LiteralStart):
                if isinstance(data[i + 1], tokens.lst.ListStart):
                    self.state = State.literal
                    return_val, j = self.create_syntax_tree(data[i + 2:])
                    self.state = State.nil
                    i += j + 1
                    tree.append(tokens.literal.Literal(return_val))
                else:
                    tree.append(tokens.literal.Literal(data[i + 1].value))
                    i += 1

            # Parses a list
            elif isinstance(data[i], tokens.lst.ListStart):
                return_val, j = self.create_syntax_tree(data[i + 1:])
                i += j
                tree.append(return_val)

            # End a list
            elif isinstance(data[i], tokens.lst.ListEnd):
                return tree, i + 1

            # Normal character
            else:
                if self.state == State.literal:
                    tree.append(data[i].value)
                else:
                    tree.append(data[i])

            i += 1

        return tree if len(tree) > 1 else (tree[0] if len(tree) > 0 else []), i

    def parse_cons(self, data):
        i = 0
        while i < len(data):
            # Parses a literal
            if isinstance(data[i], tokens.lst.Lst):
                return_val = self.parse_cons(data[i])
                data[i] = return_val
            elif isinstance(data[i], tokens.lst.Cons):
                data[i] = tokens.lst.Lst(tokens.symbol.Symbol("cons"), data[i - 1], data[i + 1])
                del data[i + 1]
                del data[i - 1]
                i -= 2

            i += 1

        return data

    def parse_buffer(self, buf):
        """
        Applies the parseToken function until the entire buffer is parsed, at which point it returns a syntax tree
        """

        if not buf.count("(") == buf.count(")"):
            raise syntaxerror.PylispSyntaxError(
                buf, "Opening brackets do not match closing brackets")

        self.position = 0
        self.state = None
        self.data = []

        token_list = []
        while self.position < len(buf):
            parsed = self.parse_token(buf[self.position:])
            token_list.extend(parsed) if isinstance(
                parsed, list) else token_list.append(parsed)

        if len(token_list) == 0 or token_list == tokens.lst.Lst(None):
            return tokens.string.String("")

        result, _ = self.create_syntax_tree(token_list)

        if isinstance(result, tokens.lst.Lst):
            result = self.parse_cons(result)

        return result
