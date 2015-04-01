from enum import Enum

from tokens.lst import Lst


class ContinuationType(Enum):
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


class Continuation(Lst):
    def __init__(self, *secList):
        Lst.__init__(self, *secList)
