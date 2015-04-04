from interpreter.read import READ
from interpreter.printer import PRINT


def rep(line, vm):
    """
    The read eval print loop
    """
    PRINT(vm.EVAL(READ(line)))
