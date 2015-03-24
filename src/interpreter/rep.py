from interpreter.read import READ
from interpreter.printer import PRINT


def rep(line, vm):
    PRINT(vm.EVAL(READ(line)))
