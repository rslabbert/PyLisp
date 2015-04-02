import tokens
from errors.symbolnotfound import SymbolNotFound
from errors.syntaxerror import PylispSyntaxError
from errors.librarynotfound import LibraryNotFound
from tokens.lst import Lst
from continuation import Continuation, ContinuationType
from env import Env
from copy import copy
from functools import partial

coreKeywords = ["define", "begin", "lambda", "let", "do",
                "if", "set!", "list", "library", "import", "export", "cond"]


class VirtualMachine():

    """Docstring for Evaluator. """

    def __init__(self, env):
        self.expr = self.kontinuation = self.vals = self.func = self.args = self.counter = self.ls = self.returnVal = self.export = None
        self.env = env

    def getRegisters(self):
        return [
            self.expr,
            self.env,
            self.kontinuation,
            self.vals,
            self.func,
            self.args,
            self.counter,
            self.ls,
            self.export]

    def setRegisters(self, registers):
        self.expr = registers[0]
        self.env = registers[1]
        self.kontinuation = registers[2]
        self.vals = registers[3]
        self.func = registers[4]
        self.args = registers[5]
        self.counter = registers[6]
        self.ls = registers[7]
        self.export = registers[8]

    def evalValue(self):
        if not isinstance(self.expr, tokens.symbol.Symbol) and not isinstance(self.expr, tokens.number.Number) and not isinstance(self.expr, Lst) and not isinstance(self.expr, tokens.string.String):
            self.vals = self.expr
            self.counter = self.evalKontinuation
            return
        elif isinstance(self.expr, tokens.symbol.Symbol):
            val = self.env.get(self.expr.value)
            if val is False:
                if val not in coreKeywords:
                    raise SymbolNotFound(self.expr.value)
                    self.counter = None
                    return

            self.vals = val
            self.counter = self.evalKontinuation
            return
        elif isinstance(self.expr, tokens.number.Number):
            try:
                self.vals = int(self.expr.value)
            except ValueError:
                self.vals = float(self.expr.value)
            self.counter = self.evalKontinuation
            return
        elif isinstance(self.expr, tokens.string.String):
            self.vals = str(self.expr.value)
            self.counter = self.evalKontinuation
            return
        elif isinstance(self.expr, Lst):
            if isinstance(self.expr.head(), tokens.symbol.Symbol) and self.expr.head().value in coreKeywords and self.env.get(self.expr.head().value, "notShadowed") == "notShadowed":
                sym = self.expr.head().value
                if sym == "lambda":
                    if len(self.expr) > 3:
                        raise PylispSyntaxError(
                            "lambda", "More than two expressions")
                    elif len(self.expr) < 3:
                        raise PylispSyntaxError(
                            "lambda", "Less than two expressions")
                    args = self.expr[1]
                    body = self.expr[2]

                    if body is None:
                        self.vals = tokens.function.Function(
                            [], args, self.env)
                    self.vals = tokens.function.Function(args, body, self.env)

                    self.counter = self.evalKontinuation
                    return
                elif sym == "let":
                    if len(self.expr) < 3:
                        raise PylispSyntaxError(
                            "let", "Less than two expressions")
                    bindings = self.expr[1]
                    body = self.expr[2]

                    if body is None:
                        self.expr = bindings
                        self.counter = self.evalKontinuation

                    bindCursor = bindings
                    bindLeft = Lst(*[x.head() for x in bindCursor])
                    bindRight = Lst(*[x.tail() for x in bindCursor])

                    self.ls = bindRight
                    self.kontinuation = Continuation(
                        ContinuationType.cLet, body, bindLeft, copy(self.env), self.kontinuation)
                    self.counter = self.evalMapValue
                    return
                elif sym == "begin":
                    if self.expr.tail() is None:
                        self.vals = None
                        self.counter = self.evalKontinuation
                        return

                    self.ls = self.expr.tail()
                    self.kontinuation = Continuation(
                        ContinuationType.cBegin, copy(self.env), self.kontinuation)
                    self.counter = self.evalMapValue
                    return
                elif sym == "if":
                    if len(self.expr) > 4:
                        raise PylispSyntaxError(
                            "if", "Too many expressions, only condition, true and false allowed")
                    elif len(self.expr) < 3:
                        raise PylispSyntaxError(
                            "if", "No true or false responses")
                    self.kontinuation = Continuation(
                        ContinuationType.cIf, self.expr[2], self.expr[3], self.env, self.kontinuation)
                    self.expr = self.expr[1]
                    self.counter = self.evalValue
                    return
                elif sym == "define" or sym == "set!":
                    if not len(self.expr) == 3:
                        raise PylispSyntaxError(
                            sym, "Too many expressions, only name and value allowed")
                    if isinstance(self.expr[1], Lst):
                        name = self.expr[1].head()
                        self.vals = tokens.function.Function(
                            self.expr[1].tail(), self.expr[2], self.env)
                        self.counter = self.evalKontinuation
                    else:
                        name = self.expr[1]
                        self.expr = self.expr[2]
                        self.counter = self.evalValue
                    if sym == "define":
                        self.kontinuation = Continuation(
                            ContinuationType.cDefine, name, self.env, self.kontinuation)
                    elif sym == "set!":
                        self.kontinuation = Continuation(
                            ContinuationType.cSet, name, self.env, self.kontinuation)
                    return
                elif sym == "list":
                    if isinstance(self.expr[1], Lst):
                        self.ls = Lst(*self.expr[1])
                    else:
                        self.ls = Lst(self.expr[1])
                    self.counter = self.evalMapValue
                    return
                elif sym == "library":
                    name = self.expr[1][0].value
                    self.expr = self.expr[2:]

                    self.kontinuation = Continuation(
                        ContinuationType.cLibrary, name, self.env, self.kontinuation)
                    self.counter = self.evalValue
                    return
                elif sym == "import":
                    name = self.expr[1].value
                    self.kontinuation = Continuation(
                        ContinuationType.cImport, name, self.env, self.kontinuation)
                    self.expr = None
                    self.counter = self.evalKontinuation
                    return
                elif sym == "export":
                    if not self.export:
                        self.export = [self.expr[1].value]
                    else:
                        self.export.append(self.expr[1].value)
                    self.counter = self.evalKontinuation
                    return
                elif sym == "cond":
                    exprs = self.expr[1:]
                    conds = Lst(*[x.head() for x in exprs])
                    rets = Lst(*[x.tail() for x in exprs])

                    self.ls = conds
                    self.kontinuation = Continuation(
                        ContinuationType.cCond, rets, self.kontinuation)
                    self.counter = self.evalMapValue
                    return
            else:
                self.kontinuation = Continuation(
                    ContinuationType.cProcFunc, self.expr.tail(), self.env, self.kontinuation)
                self.expr = self.expr.head()
                return

    def evalKontinuation(self):
        k = self.kontinuation.head()
        if k == ContinuationType.cEmpty:
            if self.returnVal is None:
                self.returnVal = self.vals

            self.counter = None
            return
        elif k == ContinuationType.cResetEnv:
            self.env = self.kontinuation[1]
            self.kontinuation = self.kontinuation[2]
            return
        elif k == ContinuationType.cLet:
            args = self.vals
            body = self.kontinuation[1]
            bindLeft = self.kontinuation[2]
            env = self.kontinuation[3]
            k = self.kontinuation[4]

            self.env.set([x.value for x in bindLeft] if len(
                bindLeft) > 1 else bindLeft[0].value, args)

            self.expr = body
            self.kontinuation = Continuation(
                ContinuationType.cResetEnv, copy(env), k)
            self.counter = self.evalValue
            return
        elif k == ContinuationType.cBegin:
            results = self.vals
            env = self.kontinuation[1]
            k = self.kontinuation[2]

            self.kontinuation = Continuation(
                ContinuationType.cResetEnv, copy(env), k)
            self.vals = results[-1] if self.vals is not None else None
            self.counter = self.evalKontinuation
            return
        elif k == ContinuationType.cIf:
            condition = self.vals
            true = self.kontinuation[1]
            false = self.kontinuation[2]
            env = self.kontinuation[3]
            k = self.kontinuation[4]

            if condition:
                self.expr = true
                self.env = env
                self.kontinuation = k
                self.counter = self.evalValue
                return
            elif false is None:
                self.kontinuation = k
                self.vals = false
                self.counter = self.evalKontinuation
                return
            else:
                self.expr = false
                self.env = env
                self.kontinuation = k
                self.counter = self.evalValue
                return
        elif k == ContinuationType.cSet or k == ContinuationType.cDefine:
            value = self.vals
            symbol = self.kontinuation[1]

            if k == ContinuationType.cSet and self.env.get(symbol.value) is False:
                raise SymbolNotFound(symbol.value)

            env = self.kontinuation[2]
            k = self.kontinuation[3]

            self.env.set(symbol.value, value)
            self.returnVal = value
            self.kontinuation = k
            self.vals = None
            self.counter = self.evalKontinuation
            return
        elif k == ContinuationType.cProcFunc:
            func = self.vals
            args = self.kontinuation[1]
            env = self.kontinuation[2]
            k = self.kontinuation[3]

            self.ls = args
            self.env = env
            self.kontinuation = Continuation(
                ContinuationType.cProcArgs, func, k)
            self.counter = self.evalMapValue
            return
        elif k == ContinuationType.cProcArgs:
            args = self.vals
            func = copy(self.kontinuation[1])
            keys = self.kontinuation[2]

            if isinstance(func, Continuation):
                self.kontinuation = func
                self.vals = args.head()
                self.counter = self.evalKontinuation
                return

            self.func = func
            self.args = args
            self.kontinuation = Continuation(
                ContinuationType.cResetEnv, copy(self.env), keys)
            self.counter = self.evalProcedure
            return
        elif k == ContinuationType.cMapValueOfStep:
            first = self.vals
            second = self.kontinuation[1]
            env = self.kontinuation[2]
            key = self.kontinuation[3]

            self.ls = second
            self.env = env
            self.kontinuation = Continuation(
                ContinuationType.cMapValueOfCons, first, key)
            self.counter = self.evalMapValue
            return
        elif k == ContinuationType.cMapValueOfCons:
            first = self.kontinuation[1]
            second = self.vals
            k = self.kontinuation[2]

            self.kontinuation = k
            if not isinstance(second, Lst):
                self.vals = Lst(first, second)
            elif len(second) > 0:
                self.vals = Lst(first, *second)
            else:
                self.vals = first
            self.counter = self.evalKontinuation
            return
        elif k == ContinuationType.cLibrary:
            name = self.kontinuation[1]
            env = self.kontinuation[2]
            k = self.kontinuation[3]
            self.kontinuation = k

            libEnv = Env()
            for i in self.export:
                libEnv.set(i, self.env[i])
                del self.env[i]

            self.export = None

            env.set(name, libEnv)
            self.env = env
            self.counter = self.evalValue
            return
        elif k == ContinuationType.cImport:
            name = self.kontinuation[1]
            env = self.kontinuation[2]
            k = self.kontinuation[3]
            self.kontinuation = k

            libEnv = Env()

            val = env.get(name)
            if val is False:
                val = libEnv.includeStandardLib(name)
                if val is False:
                    raise LibraryNotFound(name)
            else:
                libEnv = val

            env.update(libEnv)

            self.env = env
            self.counter = self.evalValue
            return
        elif k == ContinuationType.cCond:
            conds = self.vals
            rets = self.kontinuation[1]
            k = self.kontinuation[2]

            for i, v in enumerate(conds):
                if v is True or v == tokens.pylSyntax.PylSyntax.sElse:
                    self.expr = rets[i]
                    break
                else:
                    self.expr = None

            self.kontinuation = k
            self.counter = self.evalValue
            return

    def evalMapValue(self):
        if self.ls is None or len(self.ls) == 0:
            self.vals = self.ls
            self.counter = self.evalKontinuation
            return
        else:
            self.expr = self.ls.head()
            self.kontinuation = Continuation(
                ContinuationType.cMapValueOfStep, self.ls.tail(), self.env, self.kontinuation)
            self.counter = self.evalValue
            return

    def evalProcedure(self):
        if isinstance(self.func, tokens.function.Function):
            self.expr = self.func.expr

            if not isinstance(self.args, Lst):
                if 1 == len(self.func.args):
                    self.env = self.func.getEnv(self.env, self.args)
                    self.counter = self.evalValue
                else:
                    self.func.env = self.func.getEnv(self.env, self.args)
                    self.func.args = self.func.args[1:]
                    self.vals = self.func
                    self.counter = self.evalKontinuation
            else:
                if len(self.args) <= len(self.func.args):
                    self.env = self.func.getEnv(self.env, *self.args)
                    self.counter = self.evalValue
                elif len(self.args) > len(self.func.args):
                    raise PylispSyntaxError("function", "Too many arguments")
                else:
                    self.func.env = self.func.getEnv(self.env, *self.args)
                    self.func.args = self.func.args[len(self.args):]
                    self.vals = self.func
                    self.counter = self.evalKontinuation

            return
        elif not hasattr(self.func, '__call__'):
            self.vals = self.func
            self.counter = self.evalKontinuation
        elif isinstance(self.func, partial):
            self.counter = self.evalKontinuation

            if not isinstance(self.args, Lst):
                if 1 == self.func.func.__code__.co_argcount - len(self.func.args):
                    self.vals = self.func(self.args)
                else:
                    self.func.args.append(self.args)
                    self.vals = self.func
            else:
                if len(self.args) <= self.func.__code__.co_argcount:
                    self.vals = self.func(*self.args)
                elif len(self.args) > len(self.func.args):
                    raise PylispSyntaxError("function", "Too many arguments")
                else:
                    self.func.args.append(*self.args)
                    self.vals = self.func
        else:
            self.counter = self.evalKontinuation

            if 1 == self.func.__code__.co_argcount:
                self.vals = self.func(self.args)
            elif len(self.args) <= self.func.__code__.co_argcount:
                self.vals = self.func(*self.args)
            elif len(self.args) > self.func.__code__.co_argcount:
                raise PylispSyntaxError("function", "Too many arguments")
            else:
                self.vals = partial(self.func, *self.args)

    def EVAL(self, expr):
        self.expr = expr
        self.kontinuation = Continuation(ContinuationType.cEmpty)
        self.counter = self.evalValue
        self.returnVal = None
        while self.counter is not None:
            self.counter()
        return self.returnVal
