from interpreter.interpreter import Interpreter


def main():

    # Main loop which prompts user for input and print the response of the input handed to the rep function
    interpreter = Interpreter()
    interpreter.cmdloop()

if __name__ == '__main__':
    main()
