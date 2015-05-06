import tokens
from errors.symbolnotfound import SymbolNotFound
from errors.syntaxerror import PylispSyntaxError
from errors.librarynotfound import LibraryNotFound
from errors.pylisptypeerror import PylispTypeError
from tokens.lst import Lst
from env import Env
from copy import deepcopy, copy
from functools import partial
import fileparser
import os


class VirtualMachine():
    """
    The main machine which evaluates the ast.
    Based on a (C)ontrol, (E)nvironment, (K)ontinuation, or CEK machine
    """

    def __init__(self, env):
        """
        In this all the registers are created
        """
        # The PyLisp expression will be evaluated into a form which the machine
        # understands
        self.expr = None

        # What to do after the current expression is handled. A list, the last
        # element is normally the next continuation. Ends in cEmpty signalling
        # end of the execution.
        self.continuation = None

        # The value(s) returned after expression is evaluated
        self.values = None

        # A function to be called. Can be either a user defined
        # function(tokens.function.Function) or a builtin
        self.func = None

        # The arguments which will be passed to self.func
        self.args = None

        # The next function to be executed, chosen from the methods of this
        # class e.g. self.evalValue
        self.counter = None

        # A list of expressions to be evaluated. It is always used in
        # conjunction with self.evalMapValue(). Used for example when
        # evaluating arguments passed to a function i.e. (+ (+ 1 2) 2) ->
        # self.list_exprs = [(+ 1 2), 2]
        self.list_exprs = None

        # A register which is used purely for the interactive prompt.
        # Represents the last value returned evaluated, thus can be used to
        # print expressions, e.g. (+ 1 2) will have a self.returnval of 3
        self.return_val = None

        # Used in conjunction with libraries, contains all the values being
        # exported.
        self.export = None

        # The environment which stores all the symbols besides core keywords.
        # It's used to evaluate symbols and variable definitions
        # e.g. number? will evaluate to lambda x: isinstance(x,
        # tokens.number.Number)
        self.env = env

        self.core_keywords = {
            "define": self.sDefine,
            "begin": self.sBegin,
            "lambda": self.sLambda,
            "let": self.sLet,
            "if": self.sIf,
            "set!": self.sDefine,
            "library": self.sLibrary,
            "import": self.sImport,
            "export": self.sExport,
            "cond": self.sCond,
            "load": self.sLoad
        }

    def get_registers(self):
        """
        Returns all the registers
        """
        return [self.expr, self.env, self.continuation, self.values, self.func,
                self.args, self.counter, self.list_exprs, self.export]

    def set_registers(self, registers):
        """
        Sets all the registers
        """
        (self.expr, self.env, self.continuation, self.values, self.func,
         self.args, self.counter, self.list_exprs, self.export) = registers

    def flatten_expression(self, expr):
        """
        Completely flattens an expression to contain no lsts. Only used to loop over expressions without using recursion
        """
        for i in expr:
            if isinstance(i, Lst):
                for j in self.flatten_expression(i):
                    yield j
            else:
                yield i

    def eval_value(self):
        """
        Evaluates the value of self.expr
        """

        # A catch all for when it is not a type evalValue supports. Just
        # returns the expr.
        if not isinstance(self.expr,
                          (tokens.symbol.Symbol, tokens.number.Number, Lst,
                           tokens.string.String, tokens.literal.Literal)):
            self.values = self.expr
            self.counter = self.eval_continuation
            return
        # If the expr is a literal, extract the value
        elif isinstance(self.expr, tokens.literal.Literal):
            self.values = self.expr.value
            self.counter = self.eval_continuation
            self.expr = None
            return
        # If it is a symbol get it from the environment. If it doesn't exist
        # and it is not a core keyword raise an error, otherwise return it
        elif isinstance(self.expr, tokens.symbol.Symbol):
            val = self.env.get(self.expr.value)
            if val == tokens.pylsyntax.PylSyntax.sNil and val not in self.core_keywords.keys():
                raise SymbolNotFound(self.expr.value)

            self.values = val
            self.counter = self.eval_continuation
            self.expr = None
            return
        # Extracts a number
        elif isinstance(self.expr, tokens.number.Number):
            self.values = self.expr.value
            self.counter = self.eval_continuation
            self.expr = None
            return
        # Extracts a string
        elif isinstance(self.expr, tokens.string.String):
            self.values = str(self.expr.value)
            self.counter = self.eval_continuation
            self.expr = None
            return
        # Deals with Lsts
        elif isinstance(self.expr, Lst):
            # If the first item is a core keyword and hasn't been shadowed by a
            # user defined function
            if len(self.expr) == 0:
                self.values = None
                self.expr = None
                self.counter = self.eval_continuation
                return
            elif (isinstance(self.expr.head(), tokens.symbol.Symbol) and
                  self.expr.head().value in self.core_keywords.keys() and self.env.get(
                      self.expr.head().value, "notShadowed") == "notShadowed"):
                sym = self.expr.head().value
                result = self.core_keywords.get(sym, self.sElse)
                result()
            else:
                self.sElse()


    def sLambda(self):
        if len(self.expr) > 3:
            raise PylispSyntaxError(
                "lambda",
                "Too many expressions, only arguments and body allowed")
        elif len(self.expr) < 3:
            raise PylispSyntaxError("lambda", "Argument and/or body needed")

        args = self.expr[1]
        body = self.expr[2]

        self.values = tokens.function.Function("lambda", args, body, Env())

        self.counter = self.eval_continuation

    def sLet(self):
        if len(self.expr) < 3:
            raise PylispSyntaxError("let", "Less than two expressions")
        bindings = self.expr[1]
        body = self.expr[2]

        # If there isn't a body then there are no bindings, so
        # shift everything
        if body is None:
            self.expr = bindings
            self.counter = self.eval_continuation
            return

        # Extract all the bindings, to then evaluate the right side
        # and assign it to the left
        bind_left = Lst(*[x.head() for x in bindings])
        bind_right = Lst(*[x[1] for x in bindings])

        self.list_exprs = bind_right
        self.continuation = Lst(self.cLet, body, bind_left, self.continuation)
        self.counter = self.eval_map_value

    def sBegin(self):
        if self.expr.tail() is None:
            self.values = None
            self.counter = self.eval_continuation
            return

        self.list_exprs = self.expr.tail()
        self.continuation = Lst(self.cBegin, self.continuation)
        self.counter = self.eval_map_value

    def sIf(self):
        if len(self.expr) > 4:
            raise PylispSyntaxError(
                "if",
                "Too many expressions, only condition, true and false allowed")
        elif len(self.expr) < 4:
            raise PylispSyntaxError("if", "No true and/or false responses")

        self.continuation = Lst(self.cIf, self.expr[2], self.expr[3],
                                self.continuation)
        self.expr = self.expr[1]
        self.counter = self.eval_value

    def sDefine(self):
        sym = self.expr.head().value
        if not len(self.expr) == 3:
            raise PylispSyntaxError(
                sym,
                "Wrong number of expressions, only name and value allowed")

        # If expr[1] is a Lst, then it's a function definition
        if isinstance(self.expr[1], Lst):
            name = self.expr[1].head()
            self.values = tokens.function.Function(name, self.expr[1].tail(),
                                                   self.expr[2], Env())
            self.counter = self.eval_continuation
        else:
            name = self.expr[1]
            self.expr = self.expr[2]
            self.counter = self.eval_value

        # Define and set are dealt with individually since set!
        # cannot change a variable which does not exist
        if sym == "define":
            self.continuation = Lst(self.cDefine, name, self.continuation)
        elif sym == "set!":
            self.continuation = Lst(self.cSet, name, self.continuation)

    def sLibrary(self):
        if len(self.expr) < 2:
            raise PylispSyntaxError("library", "No name provided")
        name = self.expr[1][0].value
        self.expr = self.expr[2:]

        self.continuation = Lst(self.cLibrary, name, deepcopy(self.env),
                                self.continuation)
        self.counter = self.eval_value

    def sImport(self):
        if len(self.expr) < 2:
            raise PylispSyntaxError("import", "No to import provided")
        name = self.expr[1].value
        self.continuation = Lst(self.cImport, name, self.env, self.continuation)
        self.expr = None
        self.counter = self.eval_continuation

    def sExport(self):
        if len(self.expr) < 2:
            raise PylispSyntaxError("export", "Nothing to export provided")
        if not self.export:
            self.export = [self.expr[1].value]
        else:
            self.export.append(self.expr[1].value)
        self.counter = self.eval_continuation

    def sCond(self):
        if len(self.expr) < 2:
            raise PylispSyntaxError("cond",
                                    "At least one test needs to be provided")
        exprs = self.expr[1:]
        conds = Lst(*[x.head() for x in exprs])
        rets = Lst(*[x.tail() for x in exprs])

        self.expr = conds.head()
        self.continuation = Lst(self.cCond, conds.tail(), rets,
                                self.continuation)
        self.counter = self.eval_value

    def sLoad(self):
        if len(self.expr) < 2:
            raise PylispSyntaxError("load", "Nothing to load provided")
        self.continuation = Lst(self.cLoad, self.expr[1].value + ".pyl",
                                self.continuation)

        self.expr = None

    def sElse(self):
        self.continuation = Lst(self.cProcFunc, self.expr.tail(),
                                self.continuation)
        self.expr = self.expr.head()

    def eval_continuation(self):
        self.continuation[0]()

    # Always the last item in the continuation
    # Signals the end of an expression
    # Ends execution
    def cEmpty(self):
        if self.return_val is None:
            self.return_val = self.values

        self.counter = None
        return

    # Used after certain expressions to reset the environment
    # This emulates local environments for functions and let expressions
    def cResetEnv(self):
        for k, v in self.continuation[1].items():
            if v == tokens.pylsyntax.PylSyntax.sNil:
                del self.env[k]
            else:
                self.env[k] = v
        self.env.update(self.continuation[1])
        self.continuation = self.continuation[2]
        return

    def cLet(self):
        args = self.values
        body = self.continuation[1]
        bind_left = self.continuation[2]
        k = self.continuation[3]

        init = {}

        for x in bind_left:
            init[x.value] = self.env.get(x.value)

        self.env.set([x.value for x in bind_left] if len(bind_left) > 1 else
                     bind_left[0].value, args)

        self.expr = body
        self.continuation = Lst(self.cResetEnv, init, k)
        self.counter = self.eval_value
        return

    def cBegin(self):
        results = self.values
        k = self.continuation[1]

        self.continuation = k
        self.values = results[-1] if self.values is not None else None
        self.counter = self.eval_continuation
        return

    def cIf(self):
        condition = self.values
        true = self.continuation[1]
        false = self.continuation[2]
        k = self.continuation[3]

        if condition:
            self.expr = true
            self.continuation = k
            self.counter = self.eval_value
            return
        elif false is None:
            self.continuation = k
            self.values = false
            self.counter = self.eval_continuation
            return
        else:
            self.expr = false
            self.continuation = k
            self.counter = self.eval_value
            return

    def cDefine(self):
        value = self.values
        symbol = self.continuation[1]

        k = self.continuation[2]

        self.env.set(symbol.value, value)
        self.return_val = value
        self.continuation = k
        self.values = None
        self.counter = self.eval_continuation
        return

    def cSet(self):
        value = self.values
        symbol = self.continuation[1]

        if self.env.get(symbol.value) == tokens.pylsyntax.PylSyntax.sNil:
            raise SymbolNotFound(symbol.value)

        k = self.continuation[2]

        self.env.set(symbol.value, value)
        self.return_val = value
        self.continuation = k
        self.values = None
        self.counter = self.eval_continuation
        return

    # The first step in evaluating a function
    # Evaluates all the arguments first to ensure that only a single value
    # is passed to the function as opposed to an expression
    def cProcFunc(self):
        func = self.values
        args = self.continuation[1]
        k = self.continuation[2]

        self.list_exprs = args
        self.continuation = Lst(self.cProcArgs, func, k)
        self.counter = self.eval_map_value
        return

    # After the arguments are evaluated the function is then set up to be
    # run by the evalProcedure function
    def cProcArgs(self):
        args = self.values
        func = copy(self.continuation[1])
        keys = self.continuation[2]

        self.func = func
        self.args = args
        self.continuation = keys
        self.counter = self.eval_procedure
        return

    # A step in evaluating more than one expression
    # Takes the first item returned puts it in a continuation then goes on
    # to evaluate the second argument
    def cMapValueOfStep(self):
        first = self.values
        second = self.continuation[1]
        k = self.continuation[2]

        self.list_exprs = second
        self.continuation = Lst(self.cMapValueOfCons, first, k)
        self.counter = self.eval_map_value
        return

    # After cMapValueOfStep has been performed and the second value does not exist anymore
    # The first and second elements are then bound together in a Lst
    def cMapValueOfCons(self):
        first = self.continuation[1]
        second = self.values
        k = self.continuation[2]

        self.continuation = k

        # Make sure that a proper Lst is returned
        if not isinstance(second, Lst):
            self.values = Lst(first, second)
        elif len(second) > 0:
            self.values = Lst(first, *second)
        else:
            self.values = Lst(first)

        self.counter = self.eval_continuation
        return

    # For definition of a library
    # It creates its own environment, then binds all the export values into it
    # Finally it adds the library to the main environment
    def cLibrary(self):
        name = self.continuation[1]
        env = self.continuation[2]
        k = self.continuation[3]
        self.continuation = k

        lib_env = Env()

        def get_dependants(expr):
            """
            Gets all the functions a function needs to run
            """
            depends = []
            if isinstance(expr, tokens.function.Function):
                for j in self.flatten_expression(expr.expr):
                    val = self.env.get(j.value)
                    if j.value not in self.core_keywords.keys() and val is not tokens.pylsyntax.PylSyntax.sNil and val is not expr:
                        if env.get(j.value) == tokens.pylsyntax.PylSyntax.sNil:
                            depends.append((j.value, val))
                            depends += get_dependants(val)

            return depends

        if self.export:
            for i in self.export:
                # Gets all the dependants and adds it to the functions environment
                if isinstance(self.env[i], tokens.function.Function):
                    for ident, val in get_dependants(self.env[i]):
                        self.env[i].env.set(ident, val)

                lib_env.set(i, self.env[i])

            self.export = None

        env.set(name, lib_env)
        self.env = env
        self.counter = self.eval_value
        return

    # Import pulls a library from either the environment or as a standard
    # library
    def cImport(self):
        name = self.continuation[1]
        env = self.continuation[2]
        k = self.continuation[3]
        self.continuation = k

        lib_env = Env()

        val = env.get(name)
        if val == tokens.pylsyntax.PylSyntax.sNil:
            vals = lib_env.include_lib(name)
            for lib in vals:
                if not lib == tokens.pylsyntax.PylSyntax.sNil:
                    if lib[0] == "py":
                        self.env.update(lib[1])
                    elif lib[0] == "pyl":
                        self.continuation = Lst(self.cLoad, lib[1],
                                                self.continuation)
        else:
            lib_env = val

        env.update(lib_env)

        self.env = env
        self.counter = self.eval_value
        return

    # Checks every condition until a true or else is found, then returns
    # the corresponding return value
    def cCond(self):
        cond = self.values
        conditions = self.continuation[1]
        return_values = self.continuation[2]
        k = self.continuation[3]

        if cond is True or cond == tokens.pylsyntax.PylSyntax.sElse:
            self.expr = return_values.head()
            self.continuation = k
        else:
            self.expr = conditions.head()
            self.continuation = Lst(self.cCond, conditions.tail(),
                                    return_values.tail(), k)

        self.counter = self.eval_value
        return

    def cLoad(self):
        name = self.continuation[1]
        k = self.continuation[2]

        env = Env()

        file_parse = fileparser.FileParser(name, VirtualMachine(env))
        file_parse.run()

        self.env.update(file_parse.vm.env)

        self.continuation = k
        self.counter = self.eval_value
        return

    def eval_map_value(self):
        """
        Evaluates multiple values in a Lst.
        Works by evaluating the first element, then returning a list with all the rest. This continues until the second list is empty.
        """
        if self.list_exprs is None or len(self.list_exprs) == 0:
            self.values = self.list_exprs
            self.counter = self.eval_continuation
            return

        else:
            self.expr = self.list_exprs.head()
            self.continuation = Lst(self.cMapValueOfStep,
                                    self.list_exprs.tail(), self.continuation)
            self.counter = self.eval_value
            return

    def eval_procedure(self):
        """
        Evaluates a function. Makes a distinction between PyLisp functions, builtins, and partials
        """

        # Handle () as an argument
        if len(Lst(*filter(lambda x: x is not None, self.args))) == 0:
            self.args = Lst()

        # A function defined in PyLisp
        if isinstance(self.func, tokens.function.Function):
            self.expr = self.func.expr

            # If the arguments are equal then evalute the function
            if len(self.args) == len(self.func.args):
                env = self.func.getEnv(*self.args)
                init = {}
                for k in env.keys():
                    init[k] = self.env.get(k)
                self.env.update(env)
                self.continuation = Lst(self.cResetEnv, init,
                                        self.continuation)
                self.counter = self.eval_value

            # If it's more than, return an error
            elif len(self.args) > len(self.func.args):
                raise PylispSyntaxError("function {}".format(self.func.value),
                                        "Too many arguments")

            # Otherwise, curry the function by setting some of the arguments
            else:
                func = deepcopy(self.func)
                func.env.update(func.getEnv(*self.args))
                func.args = func.args[len(self.args):]
                self.values = func
                self.counter = self.eval_continuation

            return

        elif isinstance(self.func, tokens.function.Builtin):
            self.counter = self.eval_continuation

            if len(self.args) == self.func.arg_len or self.func.has_unpack_args:
                try:
                    self.values = self.func(*self.args)
                except TypeError:
                    raise PylispTypeError(self.func, *self.args)

            elif len(self.args) > self.func.arg_len:
                raise PylispSyntaxError("function {}".format(self.func),
                                        "Too many arguments")
            else:
                self.values = self.func
                self.values.args += tuple(self.args)
                self.values.arg_len -= 1

        # Just a single token
        elif len(self.args) > 0:
            raise PylispTypeError(
                self.func, *self.args,
                msg=" because {} is not a function".format(self.func))
        else:
            self.values = self.func
            self.counter = self.eval_continuation

    def evaluate(self, expr):
        """
        Main loop. Sets the proper variables, then runs self.counter until it is None, then returns the returnVal register
        """
        self.expr = expr
        self.continuation = Lst(self.cEmpty)
        self.counter = self.eval_value
        self.return_val = None
        while self.counter is not None:
            self.counter()
        return self.return_val
