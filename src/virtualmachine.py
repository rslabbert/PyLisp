import tokens
from errors.symbolnotfound import SymbolNotFound
from errors.syntaxerror import PylispSyntaxError
from errors.librarynotfound import LibraryNotFound
from tokens.lst import Lst
from continuation import Continuation, ContinuationType
from env import Env
from copy import deepcopy
from functools import partial

coreKeywords = ["define", "begin", "lambda", "let", "do", "if", "set!", "list",
                "library", "import", "export", "cond"]


class VirtualMachine():

    """
    The main machine which evaluates the ast.
    Based on a (C)ontrol, (E)nvironment, (K)ontinuation, or CEK machine, the vm works by holding a number of registers.
    The machine is implemented as a continuous loop which continues to execute until self.counter == None. While executing it runs self.counter()
    This implementation provides speed, recursion(tail loop optimisation), and easy addition of new features.
    """

    def __init__(self, env):
        self.expr = self.continuation = self.vals = self.func = self.args = self.counter = self.ls = self.returnVal = self.export = None
        self.env = env

    def getRegisters(self):
        """
        Returns all the registers
        """
        return [self.expr, self.env, self.continuation, self.vals, self.func,
                self.args, self.counter, self.ls, self.export]

    def setRegisters(self, registers):
        """
        Sets all the registers
        """
        self.expr = registers[0]
        self.env = registers[1]
        self.continuation = registers[2]
        self.vals = registers[3]
        self.func = registers[4]
        self.args = registers[5]
        self.counter = registers[6]
        self.ls = registers[7]
        self.export = registers[8]

    def evalValue(self):
        """
        Evaluates the value of self.expr
        """
        # A catch all for when it is not a type evalValue supports. Just
        # returns the expr.
        if not isinstance(self.expr,
                          (tokens.symbol.Symbol, tokens.number.Number, Lst,
                           tokens.string.String, tokens.literal.Literal)):
            self.vals = self.expr
            self.counter = self.evalContinuation
            return
        # If the expr is a literal, extract the value
        elif isinstance(self.expr, tokens.literal.Literal):
            self.vals = self.expr.value
            self.counter = self.evalContinuation
            return
        # If it is a symbol get it from the environment. If it doesn't exist
        # and it is not a core keyword raise an error, otherwise return it
        elif isinstance(self.expr, tokens.symbol.Symbol):
            val = self.env.get(self.expr.value)
            if val is False and val not in coreKeywords:
                raise SymbolNotFound(self.expr.value)

            self.vals = val
            self.counter = self.evalContinuation
            return
        # Extracts a number
        elif isinstance(self.expr, tokens.number.Number):
            self.vals = self.expr.value
            self.counter = self.evalContinuation
            return
        # Extracts a string
        elif isinstance(self.expr, tokens.string.String):
            self.vals = str(self.expr.value)
            self.counter = self.evalContinuation
            return
        # Deals with Lsts
        elif isinstance(self.expr, Lst):
            # If the first item is a core keyword and hasn't been shadowed by a
            # user defined function
            if (isinstance(self.expr.head(), tokens.symbol.Symbol)
                    and self.expr.head().value in coreKeywords
                    and self.env.get(self.expr.head().value, "notShadowed") == "notShadowed"):

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

                    # If body is None, then the lambda doesn't have arguments,
                    # so make the body the arguments
                    if body is None:
                        self.vals = tokens.function.Function(
                            [], args, self.env)
                    else:
                        self.vals = tokens.function.Function(
                            args, body, self.env)

                    self.counter = self.evalContinuation
                    return

                elif sym == "let":
                    if len(self.expr) < 3:
                        raise PylispSyntaxError("let",
                                                "Less than two expressions")
                    bindings = self.expr[1]
                    body = self.expr[2]

                    # If there isn't a body then there are no bindings, so
                    # shift everything
                    if body is None:
                        self.expr = bindings
                        self.counter = self.evalContinuation
                        return

                    # Extract all the bindings, to then evaluate the right side
                    # and assign it to the left
                    bindCursor = bindings
                    bindLeft = Lst(*[x.head() for x in bindCursor])
                    bindRight = Lst(*[x.tail() for x in bindCursor])

                    self.ls = bindRight
                    self.continuation = Continuation(ContinuationType.cLet,
                                                     body, bindLeft,
                                                     deepcopy(self.env),
                                                     self.continuation)
                    self.counter = self.evalMapValue
                    return

                elif sym == "begin":
                    if self.expr.tail() is None:
                        self.vals = None
                        self.counter = self.evalContinuation
                        return

                    self.ls = self.expr.tail()
                    self.continuation = Continuation(ContinuationType.cBegin,
                                                     deepcopy(self.env),
                                                     self.continuation)
                    self.counter = self.evalMapValue
                    return

                elif sym == "if":
                    if len(self.expr) > 4:
                        raise PylispSyntaxError("if",
                                                "Too many expressions, only condition, true and false allowed")
                    elif len(self.expr) < 3:
                        raise PylispSyntaxError("if",
                                                "No true or false responses")

                    self.continuation = Continuation(ContinuationType.cIf,
                                                     self.expr[2],
                                                     self.expr[3], self.env,
                                                     self.continuation)
                    self.expr = self.expr[1]
                    self.counter = self.evalValue
                    return

                elif sym == "define" or sym == "set!":
                    if not len(self.expr) == 3:
                        raise PylispSyntaxError(sym,
                                                "Too many expressions, only name and value allowed")

                    # If expr[1] is a Lst, then it's a function definition
                    if isinstance(self.expr[1], Lst):
                        name = self.expr[1].head()
                        self.vals = tokens.function.Function(
                            self.expr[1].tail(), self.expr[2], self.env)
                        self.counter = self.evalContinuation
                    else:
                        name = self.expr[1]
                        self.expr = self.expr[2]
                        self.counter = self.evalValue

                    # Define and set are dealt with individually since set!
                    # cannot change a variable which does not exist
                    if sym == "define":
                        self.continuation = Continuation(ContinuationType.cDefine,
                                                         name, self.env,
                                                         self.continuation)
                    elif sym == "set!":
                        self.continuation = Continuation(ContinuationType.cSet,
                                                         name, self.env,
                                                         self.continuation)
                    return

                elif sym == "list":
                    if isinstance(self.expr[1], Lst):
                        self.ls = Lst(*self.expr[1])
                    else:
                        # Make sure to not have a list of a list with just one
                        # element in it
                        self.ls = Lst(self.expr[1])
                    self.counter = self.evalMapValue
                    return

                elif sym == "library":
                    name = self.expr[1][0].value
                    self.expr = self.expr[2:]

                    self.continuation = Continuation(ContinuationType.cLibrary,
                                                     name, self.env,
                                                     self.continuation)
                    self.counter = self.evalValue
                    return

                elif sym == "import":
                    name = self.expr[1].value
                    self.continuation = Continuation(ContinuationType.cImport,
                                                     name, self.env,
                                                     self.continuation)
                    self.expr = None
                    self.counter = self.evalContinuation
                    return

                elif sym == "export":
                    if not self.export:
                        self.export = [self.expr[1].value]
                    else:
                        self.export.append(self.expr[1].value)
                    self.counter = self.evalContinuation
                    return

                elif sym == "cond":
                    exprs = self.expr[1:]
                    conds = Lst(*[x.head() for x in exprs])
                    rets = Lst(*[x.tail() for x in exprs])

                    self.ls = conds
                    self.continuation = Continuation(ContinuationType.cCond,
                                                     rets, self.continuation)
                    self.counter = self.evalMapValue
                    return

            else:
                self.continuation = Continuation(ContinuationType.cProcFunc,
                                                 self.expr.tail(), self.env,
                                                 self.continuation)
                self.expr = self.expr.head()
                return

    def evalContinuation(self):
        """
        Evaluates the next item in the continuation by looking at the first argument which is a ContinuationType.
        """
        k = self.continuation.head()

        # Always the last item in the continuation
        # Signals the end of an expression
        # Ends execution
        if k == ContinuationType.cEmpty:
            if self.returnVal is None:
                self.returnVal = self.vals

            self.counter = None
            return

        # Used after certain expressions to reset the environment
        # This emulates local environments for functions and let expressions
        elif k == ContinuationType.cResetEnv:
            self.env = self.continuation[1]
            self.continuation = self.continuation[2]
            return

        elif k == ContinuationType.cLet:
            args = self.vals
            body = self.continuation[1]
            bindLeft = self.continuation[2]
            env = self.continuation[3]
            k = self.continuation[4]

            self.env.set([x.value for x in bindLeft] if len(bindLeft) > 1 else
                         bindLeft[0].value, args)

            self.expr = body
            self.continuation = Continuation(ContinuationType.cResetEnv,
                                             deepcopy(env), k)
            self.counter = self.evalValue
            return

        elif k == ContinuationType.cBegin:
            results = self.vals
            env = self.continuation[1]
            k = self.continuation[2]

            self.continuation = Continuation(ContinuationType.cResetEnv,
                                             deepcopy(env), k)
            self.vals = results[-1] if self.vals is not None else None
            self.counter = self.evalContinuation
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
                self.counter = self.evalContinuation
                return
            else:
                self.expr = false
                self.env = env
                self.continuation = k
                self.counter = self.evalValue
                return

        elif k == ContinuationType.cSet or k == ContinuationType.cDefine:
            value = self.vals
            symbol = self.continuation[1]

            if k == ContinuationType.cSet and self.env.get(
                    symbol.value) is False:
                raise SymbolNotFound(symbol.value)

            env = self.continuation[2]
            k = self.continuation[3]

            self.env.set(symbol.value, value)
            self.returnVal = value
            self.continuation = k
            self.vals = None
            self.counter = self.evalContinuation
            return

        # The first step in evaluating a function
        # Evaluates all the arguments first to ensure that only a single value
        # is passed to the function as opposed to an expression
        elif k == ContinuationType.cProcFunc:
            func = self.vals
            args = self.continuation[1]
            env = self.continuation[2]
            k = self.continuation[3]

            self.ls = args
            self.continuation = Continuation(
                ContinuationType.cProcArgs, func, k)
            self.env = env
            self.counter = self.evalMapValue
            return

        # After the arguments are evaluated the function is then set up to be
        # run by the evalProcedure function
        elif k == ContinuationType.cProcArgs:
            args = self.vals
            func = deepcopy(self.continuation[1])
            keys = self.continuation[2]

            self.func = func
            self.args = args
            self.continuation = Continuation(
                ContinuationType.cResetEnv, deepcopy(self.env), keys)
            self.counter = self.evalProcedure
            return

        # A step in evaluating more than one expression
        # Takes the first item returned puts it in a continuation then goes on
        # to evaluate the second argument
        elif k == ContinuationType.cMapValueOfStep:
            first = self.vals
            second = self.continuation[1]
            env = self.continuation[2]
            k = self.continuation[3]

            self.ls = second
            self.env = env
            self.continuation = Continuation(ContinuationType.cMapValueOfCons,
                                             first, k)
            self.counter = self.evalMapValue
            return

        # After cMapValueOfStep has been performed and the second value does not exist anymore
        # The first and second elements are then bound together in a Lst
        elif k == ContinuationType.cMapValueOfCons:
            first = self.continuation[1]
            second = self.vals
            k = self.continuation[2]

            self.continuation = k

            # Make sure that a proper Lst is returned
            if not isinstance(second, Lst):
                self.vals = Lst(first, second)
            elif len(second) > 0:
                self.vals = Lst(first, *second)
            else:
                self.vals = first

            self.counter = self.evalContinuation
            return

        # For definition of a library
        # It creates its own environment, then binds all the export values into it
        # Finally it adds the library to the main environment
        elif k == ContinuationType.cLibrary:
            name = self.continuation[1]
            env = self.continuation[2]
            k = self.continuation[3]
            self.continuation = k

            libEnv = Env()
            for i in self.export:
                libEnv.set(i, self.env[i])
                del self.env[i]

            self.export = None

            env.set(name, libEnv)
            self.env = env
            self.counter = self.evalValue
            return

        # Import pulls a library from either the environment or as a standard
        # library
        elif k == ContinuationType.cImport:
            name = self.continuation[1]
            env = self.continuation[2]
            k = self.continuation[3]
            self.continuation = k

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

        # Checks every condition until a true or else is found, then returns
        # the corresponding return value
        elif k == ContinuationType.cCond:
            conds = self.vals
            rets = self.continuation[1]
            k = self.continuation[2]

            for i, v in enumerate(conds):
                if v is True or v == tokens.pylSyntax.PylSyntax.sElse:
                    self.expr = rets[i]
                    break
                else:
                    self.expr = None

            self.continuation = k
            self.counter = self.evalValue
            return

    def evalMapValue(self):
        """
        Evaluates multiple values in a Lst.
        Works by evaluating the first element, then returning a list with all the rest. This continues until the second list is empty.
        """
        if self.ls is None or len(self.ls) == 0:
            self.vals = self.ls
            self.counter = self.evalContinuation
            return

        else:
            self.expr = self.ls.head()
            self.continuation = Continuation(ContinuationType.cMapValueOfStep,
                                             self.ls.tail(), self.env,
                                             self.continuation)
            self.counter = self.evalValue
            return

    def evalProcedure(self):
        """
        Evaluates a function. Makes a distinction between PyLisp functions, builtins, and partials
        """

        if not isinstance(self.args, Lst):
            self.args = Lst(self.args)

        # A function defined in PyLisp
        if isinstance(self.func, tokens.function.Function):
            self.expr = self.func.expr

            # If the arguments are equal then evalute the function
            if len(self.args) == len(self.func.args):
                self.env = self.func.getEnv(self.env, *self.args)
                self.counter = self.evalValue

            # If it's more than, return an error
            elif len(self.args) > len(self.func.args):
                raise PylispSyntaxError("function", "Too many arguments")

            # Otherwise, curry the function by setting some of the arguments
            else:
                func = deepcopy(self.func)
                func.env = func.getEnv(self.env, *self.args)
                func.args = func.args[len(self.args):]
                self.vals = func
                self.counter = self.evalContinuation

            return

        # If the function doesn't have a __call__ attr, then it's just a single token i.e. 2
        # This comes after tokens.function.Function, since that doens't have a
        # call attr
        elif not hasattr(self.func, '__call__'):
            self.vals = self.func
            self.counter = self.evalContinuation

        # If the function had been previously curried, handle that
        elif isinstance(self.func, partial):
            self.counter = self.evalContinuation

            if len(self.args) == self.func.__code__.co_argcount:
                self.vals = self.func(*self.args)

            elif len(self.args) > len(self.func.args):
                raise PylispSyntaxError("function", "Too many arguments")

            else:
                func = deepcopy(self.func)
                func.args.append(*self.args)
                self.vals = func

        # Otherwise it's a builtin function that can be called normally
        else:
            self.counter = self.evalContinuation

            if len(self.args) == self.func.__code__.co_argcount:
                self.vals = self.func(*self.args)
            elif len(self.args) > self.func.__code__.co_argcount:
                raise PylispSyntaxError("function", "Too many arguments")
            else:
                self.vals = partial(self.func, *self.args)

    def EVAL(self, expr):
        """
        Main loop. Sets the proper variables, then runs self.counter until it is None, then returns the returnVal register
        """
        self.expr = expr
        self.continuation = Continuation(ContinuationType.cEmpty)
        self.counter = self.evalValue
        self.returnVal = None
        while self.counter is not None:
            self.counter()
        return self.returnVal
