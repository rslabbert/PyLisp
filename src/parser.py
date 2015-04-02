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

    """Every type which a token can embody"""
    nil = 0
    comment = 1
    string = 2
    symbol = 3
    num = 4
    literal = 5


class Parser:

    """Class responsible for parsing user input"""

    def __init__(self):
        self.state = State.nil
        self.data = []
        self.position = 0

    def isOperator(self, string):
        """Checks if the character provided is a operator"""
        return ["+",
                "-",
                "*",
                "/",
                "^",
                "%",
                "=",
                ">",
                "<",
                ">=",
                "<=",
                "?",
                "!",
                "-",
                "#",
                ":",
                ";",
                "$",
                "&",
                ".",
                "@",
                "_",
                "~"].__contains__(string)

    def parseToken(self, buf):
        """Loops through a buffer and returns the first token"""
        currentToken = ""
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
                elif c == ")":
                    return tokens.lst.ListEnd()
                elif c.isalpha() or self.isOperator(c):
                    self.state = State.symbol
                elif c.isdigit():
                    self.state = State.num

            # Parses a string
            elif self.state == State.string:
                if c == '"':
                    return tokens.string.String(currentToken)
                elif c.isalnum() or c.isspace() or self.isOperator(c):
                    currentToken += c

            # Parses a symbol or number
            if self.state == State.symbol:
                if c.isspace() or c == "\n":
                    return tokens.symbol.Symbol(currentToken)
                elif c == "(" or c == ")":
                    self.position -= 1
                    return tokens.symbol.Symbol(currentToken)
                else:
                    currentToken += c

            elif self.state == State.num:
                if c.isspace() or c == "\n":
                    return tokens.number.Number(currentToken)
                elif c == "(" or c == ")":
                    self.position -= 1
                    return tokens.number.Number(currentToken)
                else:
                    currentToken += c

        # Handles end of buffer strings not being closed or symbols being at
        # end
        if self.state == State.symbol:
            return tokens.symbol.Symbol(currentToken)
        if self.state == State.num:
            return tokens.number.Number(currentToken)

        if self.state == State.string:
            print("String not closed before newline")
            return False

    def createSyntaxTree(self, data):
        """Takes a parsed buffer and returns a syntax tree where parens are replaced with lists containing the items between them"""
        tree = tokens.lst.Lst()
        i = 0
        while i < len(data):
            if isinstance(data[i], tokens.literal.LiteralStart):
                if isinstance(data[i + 1], tokens.lst.ListStart):
                    self.state = State.literal
                    returnVal, j = self.createSyntaxTree(data[i + 2:])
                    self.state = State.nil
                    i += j
                    tree.append(tokens.literal.Literal(returnVal))
                else:
                    tree.append(tokens.literal.Literal(data[i].value))
                    i += 1

            elif isinstance(data[i], tokens.lst.ListStart):
                returnVal, j = self.createSyntaxTree(data[i + 1:])
                i += j
                tree.append(returnVal)

            elif isinstance(data[i], tokens.lst.ListEnd):
                return tree, i + 1

            else:
                if self.state == State.literal:
                    tree.append(data[i].value)
                else:
                    tree.append(data[i])

            i += 1

        return (tree if len(tree) > 1 else (tree[0] if len(tree) > 0 else []), i)

    def parseBuffer(self, buf):
        """Applies the parseToken function until the entire buffer is parsed, at which point it returns a syntax tree"""

        if not buf.count("(") == buf.count(")"):
            raise syntaxerror.PylispSyntaxError(
                buf, "Opening brackets do not match closing brackets")

        self.position = 0
        self.state = None
        self.data = []

        tokenList = []
        while self.position < len(buf):
            tokenList.append(self.parseToken(buf[self.position:]))

        if tokenList == [] or tokenList == [None]:
            return tokens.string.String("")

        result, _ = self.createSyntaxTree(tokenList)
        return result

    def prettyPrint(self, buf):
        for i in buf:
            if i.typ == State.listStart:
                print("(", end=" ")
            elif i.typ == State.listEnd:
                print(")", end=" ")
            else:
                print(i.value, end=" ")
        print()
