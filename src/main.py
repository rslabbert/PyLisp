import sys


def main():
    if len(sys.argv) == 1:
        from interpreter.interpreter import Interpreter

        # Main loop which prompts user for input and print the response of the input handed to the rep function
        interpreter = Interpreter()
        interpreter.cmdloop()
    else:
        from fileParser import FileParser

        parser = FileParser(sys.argv[1])
        parser.run()

if __name__ == '__main__':
    main()
