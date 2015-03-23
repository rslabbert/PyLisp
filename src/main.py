import sys

from interpreter.interpreter import Interpreter
from fileParser import FileParser


def main():
    if len(sys.argv) == 1:
        # Main loop which prompts user for input and print the response of the input handed to the rep function
        interpreter = Interpreter()
        interpreter.cmdloop()
    else:
        parser = FileParser(sys.argv[1])
        parser.run()

if __name__ == '__main__':
    main()
