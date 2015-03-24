import tokens
import core
from enum import Enum


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


class Continuation(list):
    def __init__(self, *secList):
        list.__init__(self, secList)


class VirtualMachine():
    """Docstring for Evaluator. """
    def __init__(self, env):
        self.expr = self.env = self.keys = self.vals = self.func = self.args = self.counter = self.ls = self.returnVal = None
        self.env = env

    def getRegisters(self):
        return [
            self.expr,
            self.env,
            self.keys,
            self.vals,
            self.func,
            self.args,
            self.counter,
            self.ls]

    def setRegisters(self, *registers):
        self.expr = self.env = self.keys = self.vals = self.func = self.args = self.counter = self.ls = registers

    def valueOf(self):
        if isinstance(self.expr, tokens.symbol.Symbol):
            val = self.env.get(self.expr.value)
            if val is None:
                if val not in core.coreKeywords:
                    self.counter = None
                    return
            self.keys = self.keys
            self.vals = val
            self.counter = self.applyKeys
            return
        elif isinstance(self.expr, tokens.number.Number):
            try:
                val = int(self.expr.value)
            except ValueError:
                val = float(self.expr.value)
            self.vals = val
            self.counter = self.applyKeys
        elif isinstance(self.expr, tokens.lst.Lst) and self.expr[0].value is not None:
            sym = self.expr[0].value
            if sym == "lambda":
                args = self.expr[1]
                body = self.expr[2]

                self.keys = self.keys
                self.vals = core.do_lambda(args, body, self.env)
                self.counter = self.applyKeys
                return
            elif sym == "let":
                bindings = self.expr[1]
                body = self.expr[2]

                bindLeft = tokens.nil.Nil
                bindRight = tokens.nil.Nil
                bindCursor = bindings
                while bindCursor is not tokens.nil.Nil:
                    bindLeft = tokens.lst.Lst(bindCursor[0][0], bindLeft)
                    bindLeft = tokens.lst.Lst(bindCursor[0][1:], bindRight)
                    bindCursor = bindCursor[1:]

                self.ls = bindRight
                self.env = self.env
                self.keys = Continuation(ContinuationType.cLet, body, bindLeft, self.env, self.keys)
                self.counter = self.mapValueOf
                return
            elif sym == "begin":
                if self.expr[1:] is None:
                    self.keys = self.keys
                    self.vals = None
                    self.counter = self.applyKeys
                    return

                self.ls = self.expr[1:]
                self.env = self.env
                self.keys = Continuation(ContinuationType.cBegin, self.keys)
                self.counter = self.mapValueOf
                return
            elif sym == "if":
                self.env = self.env
                self.keys = Continuation(ContinuationType.cIf, self.expr[2], self.expr[3], self.env, self.keys)
                self.expr = self.expr[1]
                self.counter = self.valueOf
                return
            elif sym == "define" or sym == "set":
                name = self.expr[1]
                self.expr = self.expr[2]
                self.env = self.env
                self.keys = Continuation(ContinuationType.cSet, name, self.env, self.keys)
                self.counter = self.valueOf
                return
            elif sym == "display":
                self.keys = Continuation(ContinuationType.cProcFunc, self.expr[1:], self.env, self.keys)
                self.expr = print
                return
            elif sym == "list":
                if isinstance(self.expr[1], tokens.lst.Lst):
                    self.vals = tokens.lst.Lst(*self.expr[1])
                else:
                    self.vals = tokens.lst.Lst(self.expr[1])
                self.counter = self.applyKeys
                return
            else:
                self.env = self.env
                self.keys = Continuation(ContinuationType.cProcFunc, self.expr[1:], self.env, self.keys)
                self.expr = self.expr[0]
                return
        else:
            self.keys = self.keys
            self.vals = self.expr
            self.counter = self.applyKeys
            return

    def applyKeys(self):
        k = self.keys[0]
        if k == ContinuationType.cEmpty:
            self.returnVal = self.vals
            self.counter = None
            return
        elif k == ContinuationType.cLet:
            args = self.vals
            body = self.keys[1]
            bindLeft = self.keys[2]
            env = self.keys[3]
            k = self.keys[4]
            self.env = env.set(bindLeft, args)
            self.expr = body

            self.keys = k
            self.counter = self.valueOf
            return
        elif k == ContinuationType.cBegin:
            results = self.vals
            k = self.keys[0]
            self.keys = k
            self.vals = results[-1]
            self.counter = self.applyKeys
            return
        elif k == ContinuationType.cIf:
            condition = self.vals
            true = self.keys[1]
            false = self.keys[2]
            env = self.keys[3]
            k = self.keys[4]

            if condition:
                self.expr = true
                self.env = env
                self.keys = k
                self.counter = self.valueOf
                return
            elif false is None:
                self.keys = k
                self.vals = false
                self.counter = self.applyKeys
                return
            else:
                self.expr = false
                self.env = env
                self.keys = k
                self.counter = self.valueOf
                return
        elif k == ContinuationType.cSet:
            value = self.vals
            symbol = self.keys[1]
            env = self.keys[2]
            k = self.keys[3]

            env.set(symbol.value, value)
            self.keys = k
            self.vals = None
            self.counter = self.applyKeys
            return
        elif k == ContinuationType.cProcFunc:
            func = self.vals
            args = self.keys[1]
            env = self.keys[2]
            k = self.keys[3]

            self.ls = args
            self.env = env
            self.keys = Continuation(ContinuationType.cProcArgs, func, k)
            self.counter = self.mapValueOf
            return
        elif k == ContinuationType.cProcArgs:
            args = self.vals
            func = self.keys[1]
            keys = self.keys[2]

            if isinstance(func, Continuation):
                self.keys = func
                self.vals = args[0]
                self.counter = self.applyKeys
                return

            self.func = func
            self.args = args
            self.keys = keys
            self.counter = self.applyProc
            return
        elif k == ContinuationType.cMapValueOfStep:
            first = self.vals
            second = self.keys[1]
            env = self.keys[2]
            key = self.keys[3]

            self.ls = second
            self.env = env
            self.keys = Continuation(ContinuationType.cMapValueOfCons, first, key)
            self.counter = self.mapValueOf
            return
        elif k == ContinuationType.cMapValueOfCons:
            first = self.keys[1]
            second = self.vals
            k = self.keys[2]

            self.keys = k
            if not hasattr(second, '__len__'):
                self.vals = tokens.lst.Lst(first, second)
            elif len(second) > 0:
                self.vals = tokens.lst.Lst(first, second)
            else:
                self.vals = first
            self.counter = self.applyKeys
            return

    def mapValueOf(self):
        if len(self.ls) == 0:
            self.keys = self.keys
            self.vals = self.ls
            self.counter = self.applyKeys
            return
        else:
            self.expr = self.ls[0]
            self.env = self.env
            self.keys = Continuation(ContinuationType.cMapValueOfStep, self.ls[1:], self.env, self.keys)
            self.counter = self.valueOf
            return

    def applyProc(self):
        if isinstance(self.func, tokens.function.Function):
            self.expr = self.func.expr

            if not hasattr(self.args, '__len__'):
                self.env = self.func.getEnv(self.env, self.args)
            else:
                self.env = self.func.getEnv(self.env, *self.args)

            self.keys = self.keys
            self.counter = self.valueOf
            return
        else:
            self.keys = self.keys
            self.counter = self.applyKeys

            if not hasattr(self.args, '__len__'):
                self.vals = self.func(self.args)
            else:
                self.vals = self.func(*self.args)

    def EVAL(self, expr):
        register = self.getRegisters()
        self.expr = expr
        self.env = self.env
        self.keys = Continuation(ContinuationType.cEmpty)
        self.counter = self.valueOf
        self.returnVal = None
        try:
            while self.counter is not None:
                self.counter()
        except Exception as e:
            print(e)
            self.setRegisters(register)
        return self.returnVal
