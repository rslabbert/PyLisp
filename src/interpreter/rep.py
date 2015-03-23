from interpreter.evaluate import EVAL
from interpreter.read import READ
from interpreter.printer import PRINT


def rep(line, env):
    PRINT(EVAL(READ(line), env))
