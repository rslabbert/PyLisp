import tokens
from tokens.lst import Lst
from enum import Enum

coreKeywords = ["define", "begin", "lambda", "let", "do", "if", "set", "list"]


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


class Continuation(Lst):
    def __init__(self, *secList):
        Lst.__init__(self, *secList)


class VirtualMachine():
    """Docstring for Evaluator. """
    def __init__(self, env):
        self.expr = self.continuation = self.vals = self.func = self.args = self.counter = self.ls = self.returnVal = None
        self.env = env

    def getRegisters(self):
        return [
            self.expr,
            self.env,
            self.continuation,
            self.vals,
            self.func,
            self.args,
            self.counter,
            self.ls]

    def setRegisters(self, *registers):
        self.expr = self.env = self.continuation = self.vals = self.func = self.args = self.counter = self.ls = registers

    def evalValue(self):
        if not isinstance(self.expr, tokens.symbol.Symbol) and not isinstance(self.expr, tokens.number.Number) and not isinstance(self.expr, Lst) and not isinstance(self.expr, tokens.string.String):
            self.vals = self.expr
            self.counter = self.evalKeys
            return
        elif isinstance(self.expr, tokens.symbol.Symbol):
            val = self.env.get(self.expr.value)
            if val is None:
                if val not in coreKeywords:
                    self.counter = None
                    return

            self.vals = val
            self.counter = self.evalKeys
            return
        elif isinstance(self.expr, tokens.number.Number):
            try:
                self.vals = int(self.expr.value)
            except ValueError:
                self.vals = float(self.expr.value)
            self.counter = self.evalKeys
            return
        elif isinstance(self.expr, tokens.string.String):
            self.vals = str(self.expr.value)
            self.counter = self.evalKeys
            return
        elif isinstance(self.expr, Lst):
            if isinstance(self.expr.head(), tokens.symbol.Symbol) and self.expr.head().value in coreKeywords and self.env.get(self.expr.head().value, "notShadowed") == "notShadowed":
                sym = self.expr.head().value
                if sym == "lambda":
                    args = self.expr[1]
                    body = self.expr[2]

                    if body is None:
                        self.vals = tokens.function.Function([], args, self.env)
                    self.vals = tokens.function.Function(args, body, self.env)

                    self.counter = self.evalKeys
                    return
                elif sym == "let":
                    bindings = self.expr[1]
                    body = self.expr[2]

                    if body is None:
                        self.expr = bindings
                        self.counter = self.applyKeys

                    bindCursor = bindings
                    bindLeft = Lst(*[x.head() for x in bindCursor])
                    bindRight = Lst(*[x.tail() for x in bindCursor])

                    self.ls = bindRight
                    self.continuation = Continuation(ContinuationType.cLet, body, bindLeft, self.env, self.continuation)
                    self.counter = self.evalMapValue
                    return
                elif sym == "begin":
                    if self.expr.tail() is None:
                        self.vals = None
                        self.counter = self.evalKeys
                        return

                    self.ls = self.expr.tail()
                    self.continuation = Continuation(ContinuationType.cBegin, self.continuation)
                    self.counter = self.evalMapValue
                    return
                elif sym == "if":
                    self.continuation = Continuation(ContinuationType.cIf, self.expr[2], self.expr[3], self.env, self.continuation)
                    self.expr = self.expr[1]
                    self.counter = self.evalValue
                    return
                elif sym == "define" or sym == "set":
                    if isinstance(self.expr[1], Lst):
                        name = self.expr[1].head()
                        self.vals = tokens.function.Function(self.expr[1].tail(), self.expr[2], self.env)
                        self.counter = self.evalKeys
                    else:
                        name = self.expr[1]
                        self.expr = self.expr[2]
                        self.counter = self.evalValue
                    self.continuation = Continuation(ContinuationType.cSet, name, self.env, self.continuation)
                    return
                elif sym == "list":
                    if isinstance(self.expr[1], Lst):
                        self.ls = Lst(*self.expr[1])
                    else:
                        self.ls = Lst(self.expr[1])
                    self.counter = self.evalMapValue
                    return
            # elif len(self.expr) == 1 and (isinstance(self.expr.head(), tokens.symbol.Symbol) or isinstance(self.expr.head(), tokens.number.Number)):
                # self.expr = self.expr.head()
            else:
                self.continuation = Continuation(ContinuationType.cProcFunc, self.expr.tail(), self.env, self.continuation)
                self.expr = self.expr.head()
                return

    def evalKeys(self):
        k = self.continuation.head()
        if k == ContinuationType.cEmpty:
            if self.returnVal is None:
                self.returnVal = self.vals

            self.counter = None
            return
        elif k == ContinuationType.cLet:
            args = self.vals
            body = self.continuation[1]
            bindLeft = self.continuation[2]
            env = self.continuation[3]
            k = self.continuation[4]

            env.set([x.value for x in bindLeft], args)

            self.expr = body
            self.env = env
            self.continuation = k
            self.counter = self.evalValue
            return
        elif k == ContinuationType.cBegin:
            results = self.vals
            k = self.continuation[1]
            self.continuation = k
            self.vals = results[-1]
            self.counter = self.evalKeys
            return
        elif k == ContinuationType.cIf:
            condition = self.vals
            true = self.continuation[1]
            false = self.continuation[2]
            env = self.continuation[3]
            k = self.continuation[4]

            if condition:
                self.expr = true
                self.env = env
                self.continuation = k
                self.counter = self.evalValue
                return
            elif false is None:
                self.continuation = k
                self.vals = false
                self.counter = self.evalKeys
                return
            else:
                self.expr = false
                self.env = env
                self.continuation = k
                self.counter = self.evalValue
                return
        elif k == ContinuationType.cSet:
            value = self.vals
            symbol = self.continuation[1]
            env = self.continuation[2]
            k = self.continuation[3]

            env.set(symbol.value, value)
            self.returnVal = value
            self.continuation = k
            self.vals = None
            self.counter = self.evalKeys
            return
        elif k == ContinuationType.cProcFunc:
            func = self.vals
            args = self.continuation[1]
            env = self.continuation[2]
            k = self.continuation[3]

            self.ls = args
            self.env = env
            self.continuation = Continuation(ContinuationType.cProcArgs, func, k)
            self.counter = self.evalMapValue
            return
        elif k == ContinuationType.cProcArgs:
            args = self.vals
            func = self.continuation[1]
            keys = self.continuation[2]

            if isinstance(func, Continuation):
                self.continuation = func
                self.vals = args.head()
                self.counter = self.evalKeys
                return

            self.func = func
            self.args = args
            self.continuation = keys
            self.counter = self.evalProcedure
            return
        elif k == ContinuationType.cMapValueOfStep:
            first = self.vals
            second = self.continuation[1]
            env = self.continuation[2]
            key = self.continuation[3]

            self.ls = second
            self.env = env
            self.continuation = Continuation(ContinuationType.cMapValueOfCons, first, key)
            self.counter = self.evalMapValue
            return
        elif k == ContinuationType.cMapValueOfCons:
            first = self.continuation[1]
            second = self.vals
            k = self.continuation[2]

            self.continuation = k
            if not hasattr(second, '__len__'):
                self.vals = Lst(first, second)
            elif len(second) > 0:
                self.vals = Lst(first, *second)
            else:
                self.vals = first
            self.counter = self.evalKeys
            return

    def evalMapValue(self):
        if self.ls is None or len(self.ls) == 0:
            self.vals = self.ls
            self.counter = self.evalKeys
            return
        else:
            self.expr = self.ls.head()
            self.continuation = Continuation(ContinuationType.cMapValueOfStep, self.ls.tail(), self.env, self.continuation)
            self.counter = self.evalValue
            return

    def evalProcedure(self):
        if isinstance(self.func, tokens.function.Function):
            self.expr = self.func.expr

            if not hasattr(self.args, '__len__'):
                self.env = self.func.getEnv(self.env, self.args)
            else:
                self.env = self.func.getEnv(self.env, *self.args)

            self.counter = self.evalValue
            return
        elif not hasattr(self.func, '__call__'):
            self.vals = self.func
            self.counter = self.evalKeys
        else:
            self.counter = self.evalKeys

            if not hasattr(self.args, '__len__'):
                self.vals = self.func(self.args)
            else:
                self.vals = self.func(*self.args)

    def EVAL(self, expr):
        register = self.getRegisters()
        self.expr = expr
        self.continuation = Continuation(ContinuationType.cEmpty)
        self.counter = self.evalValue
        self.returnVal = None
        try:
            while self.counter is not None:
                self.counter()
        except Exception:
            import sys
            import traceback
            traceback.print_exc(file=sys.stdout)
            self.setRegisters(register)
        return self.returnVal
