from enum import Enum

from tokens.lst import Lst


class ContinuationType(Enum):

    """
    An enum which provides all the states the current continuation can be in
    """
    cEmpty = 0
    cLet = 1
    cBegin = 2
    cIf = 3
    cSet = 4
    cProcKeys = 5
    cProcVals = 6
    cProcFunc = 7
    cProcArgs = 8
    cMapValueOfCons = 9
    cMapValueOfStep = 10
    cLibrary = 11
    cImport = 12
    cResetEnv = 13
    cDefine = 14
    cCond = 15


class Continuation(Lst):

    """
    A continuation is a Lst which is used to represent a chain of actions the virtual machine has to return to after the current task is complete
    """

    def __init__(self, *secList):
        Lst.__init__(self, *secList)
