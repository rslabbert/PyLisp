from env import Env
from evaluate import EVAL
from read import READ
from printer import PRINT


def rep(inp, env):
    """Hands interpreter input to the read, eval, and print functions"""
    return PRINT(EVAL(READ(inp), env))


def main():
    # Gets the user's name from the environment for use in the shell
    from os import environ
    username = environ["USER"]

    # Sets the global variable environment to the standard set
    env = Env()
    env.setToStandardEnv()

    # Main loop which prompts user for input and print the response of the input handed to the rep function
    inp = "(define (fac n) (if (= n 1) n (* n (fac (- n 1)))))"
    print(PRINT(EVAL(READ(inp), env)))

    inp = "fac 5"
    print(PRINT(EVAL(READ(inp), env)))


if __name__ == '__main__':
    main()