from copy import deepcopy, copy

from env import Env
import errors.symbolnotfound
import errors.pylisptypeerror
import fileparser
import tokens


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
        # element is normally the next kontinuation. Ends in cEmpty signalling
        # end of the execution.
        self.kontinuation = None

        # The value(s) returned after expression is evaluated
        self.values = None

        # A function to be called. Can be either a user defined
        # function(tokens.function.Function) or a builtin
        self.func = None

        # The arguments which will be passed to self.func
        self.args = None

        # The next function to be executed, chosen from the methods of this
        # class e.g. self.evalValue
        self.control = None

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

        # Syntactic keywords which are implemented on a python level instead of on a pylisp level
        self.core_keywords = {
            "define": self.s_define,
            "begin": self.s_begin,
            "lambda": self.s_lambda,
            "let": self.s_let,
            "if": self.s_if,
            "set!": self.s_define,
            "library": self.s_library,
            "import": self.s_import,
            "export": self.s_export,
            "cond": self.s_cond,
            "load": self.s_load
        }

    def get_registers(self):
        """
        Returns all the registers
        """
        return [self.expr, self.env, self.kontinuation, self.values, self.func,
                self.args, self.control, self.list_exprs, self.export]

    def set_registers(self, registers):
        """
        Sets all the registers
        """
        (self.expr, self.env, self.kontinuation, self.values, self.func,
         self.args, self.control, self.list_exprs, self.export) = registers

    def flatten_expression(self, expr):
        """
        Completely flattens an expression to contain no lsts. Only used to loop over expressions without using recursion
        """
        for i in expr:
            if isinstance(i, list):
                for j in self.flatten_expression(i):
                    yield j
            else:
                yield i

    def get_dependants(self, expr, env):
        """
        Gets all the functions a function needs to run
        """
        depends = []
        if isinstance(expr, tokens.function.Function):
            for j in self.flatten_expression(expr.expr):
                val = self.env.get(j.value)
                if j.value not in self.core_keywords.keys(
                ) and val is not tokens.pylsyntax.PylSyntax.sNil and val is not expr:
                    if env.get(j.value) == tokens.pylsyntax.PylSyntax.sNil:
                        depends.append((j.value, val))
                        depends += self.get_dependants(val, env)

        return depends

    def eval_value(self):
        """
        Evaluates the value of self.expr
        """

        # A catch all for when it is not a type evalValue supports. Just
        # returns the expr.
        if not isinstance(self.expr,
                          (tokens.symbol.Symbol, tokens.number.Number, list,
                           tokens.string.String, tokens.literal.Literal)):
            self.values = self.expr
            self.control = self.eval_kontinuation
            return
        # If the expr is a literal, extract the value
        elif isinstance(self.expr, tokens.literal.Literal):
            self.values = self.expr.value
            self.control = self.eval_kontinuation
            self.expr = None
            return
        # If it is a symbol get it from the environment. If it doesn't exist
        # and it is not a core keyword raise an error, otherwise return it
        elif isinstance(self.expr, tokens.symbol.Symbol):
            val = self.env.get(self.expr.value)
            if val == tokens.pylsyntax.PylSyntax.sNil:
                if self.expr.value in self.core_keywords.keys():
                    self.expr = [self.expr]
                    return
                else:
                    raise errors.symbolnotfound.SymbolNotFound(self.expr.value)

            self.values = val
            self.control = self.eval_kontinuation
            self.expr = None
            return
        # Extracts a number
        elif isinstance(self.expr, tokens.number.Number):
            self.values = self.expr.value
            self.control = self.eval_kontinuation
            self.expr = None
            return
        # Extracts a string
        elif isinstance(self.expr, tokens.string.String):
            self.values = str(self.expr.value)
            self.control = self.eval_kontinuation
            self.expr = None
            return
        # Deals with Lsts
        elif isinstance(self.expr, list):
            # If the first item is a core keyword and hasn't been shadowed by a
            # user defined function
            if len(self.expr) == 0:
                self.values = None
                self.expr = None
                self.control = self.eval_kontinuation
                return
            elif (isinstance(self.expr[0], tokens.symbol.Symbol) and
                  self.expr[0].value in self.core_keywords.keys() and
                  self.env.get(self.expr[0].value,
                               "notShadowed") == "notShadowed"):
                sym = self.expr[0].value
                self.control = self.core_keywords.get(sym, self.s_else)
            else:
                self.control = self.s_else


    ################################################################################
    # Lambda
    ################################################################################
    def s_lambda(self):
        if len(self.expr) > 3:
            raise errors.syntaxerror.PylispSyntaxError(
                "lambda",
                "Too many expressions, only arguments and body allowed")
        elif len(self.expr) < 3:
            raise errors.syntaxerror.PylispSyntaxError(
                "lambda", "Argument and/or body needed")

        args = self.expr[1]
        body = self.expr[2]

        self.values = tokens.function.Function("lambda", args, body, Env())

        self.control = self.eval_kontinuation


    ################################################################################
    # Let
    ################################################################################
    def s_let(self):
        if len(self.expr) < 3:
            raise errors.syntaxerror.PylispSyntaxError(
                "let", "Less than two expressions")
        bindings = self.expr[1]
        body = self.expr[2]

        # If there isn't a body then there are no bindings, so
        # shift everything
        if body is None:
            self.expr = bindings
            self.control = self.eval_kontinuation
            return

        # Extract all the bindings, to then evaluate the right side
        # and assign it to the left
        if len(bindings) > 1:
            bind_left = [x[0] for x in bindings]
            bind_right = [x[1] for x in bindings]

            self.list_exprs = bind_right
            self.kontinuation = [self.c_let, body, bind_left,
                                    self.kontinuation]
            self.control = self.eval_map_value
        else:
            self.kontinuation = [self.c_let, body, [bindings[0][0]],
                                    self.kontinuation]
            self.expr = [bindings[0][1]]
            self.control = self.eval_value

    def c_let(self):
        args = self.values
        body = self.kontinuation[1]
        bind_left = self.kontinuation[2]
        k = self.kontinuation[3]

        init = {}

        for x in bind_left:
            init[x.value] = self.env.get(x.value)

        self.env.set([x.value for x in bind_left] if len(bind_left) > 1 else
                     bind_left[0].value, args)

        self.expr = body
        self.kontinuation = [self.c_reset_env, init, k]
        self.control = self.eval_value
        return


    ################################################################################
    # Begin
    ################################################################################
    def s_begin(self):
        if self.expr[1:] is None:
            self.values = None
            self.control = self.eval_kontinuation
            return

        self.list_exprs = self.expr[1:]
        self.kontinuation = [self.c_begin, self.kontinuation]
        self.control = self.eval_map_value

    def c_begin(self):
        results = self.values
        k = self.kontinuation[1]

        self.kontinuation = k
        self.values = results[-1] if self.values is not None else None
        self.control = self.eval_kontinuation
        return


    ################################################################################
    # If
    ################################################################################
    def s_if(self):
        if len(self.expr) > 4:
            raise errors.syntaxerror.PylispSyntaxError(
                "if",
                "Too many expressions, only condition, true and false allowed")
        elif len(self.expr) < 4:
            raise errors.syntaxerror.PylispSyntaxError(
                "if", "No true and/or false responses")

        self.kontinuation = [self.c_if, self.expr[2], self.expr[3],
                                self.kontinuation]
        self.expr = self.expr[1]
        self.control = self.eval_value

    def c_if(self):
        condition = self.values
        true = self.kontinuation[1]
        false = self.kontinuation[2]
        k = self.kontinuation[3]

        if condition:
            self.expr = true
            self.kontinuation = k
            self.control = self.eval_value
            return
        else:
            self.expr = false
            self.kontinuation = k
            self.control = self.eval_value
            return


    ################################################################################
    # Define Set
    ################################################################################
    def s_define(self):
        sym = self.expr[0].value
        if not len(self.expr) == 3:
            raise errors.syntaxerror.PylispSyntaxError(
                sym,
                "Wrong number of expressions, only name and value allowed")

        # If expr[1] is a Lst, then it's a function definition
        if isinstance(self.expr[1], list):
            name = self.expr[1][0]
            self.values = tokens.function.Function(name, self.expr[1][1:],
                                                   self.expr[2], Env())
            self.control = self.eval_kontinuation
        else:
            name = self.expr[1]
            self.expr = self.expr[2]
            self.control = self.eval_value

        # Define and set are dealt with individually since set!
        # cannot change a variable which does not exist
        if sym == "define":
            self.kontinuation = [self.c_define, name, self.kontinuation]
        elif sym == "set!":
            self.kontinuation = [self.c_set, name, self.kontinuation]

    def c_define(self):
        value = self.values
        symbol = self.kontinuation[1]

        k = self.kontinuation[2]

        self.env.set(symbol.value, value)
        self.return_val = value
        self.kontinuation = k
        self.values = None
        self.control = self.eval_kontinuation
        return

    def c_set(self):
        value = self.values
        symbol = self.kontinuation[1]

        if self.env.get(symbol.value) == tokens.pylsyntax.PylSyntax.sNil:
            raise errors.symbolnotfound.SymbolNotFound(symbol.value)

        k = self.kontinuation[2]

        self.env.set(symbol.value, value)
        self.return_val = value
        self.kontinuation = k
        self.values = None
        self.control = self.eval_kontinuation
        return


    ################################################################################
    # Library
    ################################################################################
    def s_library(self):
        if len(self.expr) < 2:
            raise errors.syntaxerror.PylispSyntaxError("library",
                                                       "No name provided")
        name = self.expr[1][0].value

        self.expr = self.expr[2:]

        self.kontinuation = [self.c_library, name, deepcopy(self.env),
                                self.kontinuation]
        self.control = self.eval_value

    # For definition of a library
    # It creates its own environment, then binds all the export values into it
    # Finally it adds the library to the main environment
    def c_library(self):
        name = self.kontinuation[1]
        env = self.kontinuation[2]
        k = self.kontinuation[3]
        self.kontinuation = k

        lib_env = Env()

        if self.export:
            for i in self.export:
                # Gets all the dependants and adds it to the functions environment
                if isinstance(self.env[i], tokens.function.Function):
                    for ident, val in self.get_dependants(self.env[i], env):
                        self.env[i].env.set(ident, val)

                lib_env.set(i, self.env[i])

            self.export = None

        env.set(name, lib_env)
        self.env = env
        self.control = self.eval_value
        return


    ################################################################################
    # Import
    ################################################################################
    def s_import(self):
        if len(self.expr) < 2:
            raise errors.syntaxerror.PylispSyntaxError("import",
                                                       "No to import provided")
        name = self.expr[1].value
        self.kontinuation = [self.c_import, name, self.env,
                                self.kontinuation]
        self.expr = None
        self.control = self.eval_kontinuation

    # Import pulls a library from either the environment or as a standard
    # library
    def c_import(self):
        name = self.kontinuation[1]
        env = self.kontinuation[2]
        k = self.kontinuation[3]
        self.kontinuation = k

        lib_env = Env()

        val = env.get(name)
        if val == tokens.pylsyntax.PylSyntax.sNil:
            vals = lib_env.include_lib(name)
            for lib in vals:
                if not lib == tokens.pylsyntax.PylSyntax.sNil:
                    if lib[0] == "py":
                        self.env.update(lib[1])
                    elif lib[0] == "pyl":
                        self.kontinuation = [self.c_load, lib[1],
                                                self.kontinuation]
        else:
            lib_env = val

        env.update(lib_env)

        self.env = env
        self.control = self.eval_value
        return


    ################################################################################
    # Export
    ################################################################################
    def s_export(self):
        if len(self.expr) < 2:
            raise errors.syntaxerror.PylispSyntaxError(
                "export", "Nothing to export provided")
        if not self.export:
            self.export = [self.expr[1].value]
        else:
            self.export.append(self.expr[1].value)
        self.control = self.eval_kontinuation


    ################################################################################
    # Cond
    ################################################################################
    def s_cond(self):
        if len(self.expr) < 2:
            raise errors.syntaxerror.PylispSyntaxError(
                "cond", "At least one test needs to be provided")
        exprs = self.expr[1:]
        conds = [x[0] for x in exprs]
        rets = [x[1:] for x in exprs]

        self.expr = conds[0]
        self.kontinuation = [self.c_cond, conds[1:], rets,
                                self.kontinuation]
        self.control = self.eval_value

    # Checks every condition until a true or else is found, then returns
    # the corresponding return value
    def c_cond(self):
        cond = self.values
        conditions = self.kontinuation[1]
        return_values = self.kontinuation[2]
        k = self.kontinuation[3]

        if cond is True or cond == tokens.pylsyntax.PylSyntax.sElse:
            self.expr = return_values[0]
            self.kontinuation = k
        elif len(conditions) > 0:
            self.expr = conditions[0]
            self.kontinuation = [self.c_cond, conditions[1:],
                                    return_values[1:], k]
        else:
            self.values = False
            self.kontinuation = k

        self.control = self.eval_value
        return


    ################################################################################
    # Load
    ################################################################################
    def s_load(self):
        if len(self.expr) < 2:
            raise errors.syntaxerror.PylispSyntaxError(
                "load", "Nothing to load provided")
        self.kontinuation = [self.c_load, self.expr[1].value + ".pyl",
                                self.kontinuation]

        self.expr = None
        self.control = self.eval_kontinuation

    def c_load(self):
        name = self.kontinuation[1]
        k = self.kontinuation[2]

        env = Env()

        file_parse = fileparser.FileParser(name, VirtualMachine(env))
        file_parse.run()

        self.env.update(file_parse.vm.env)

        self.kontinuation = k
        self.control = self.eval_value
        return

    def s_else(self):
        self.kontinuation = [self.c_proc_func, self.expr[1:],
                                self.kontinuation]
        self.expr = self.expr[0]
        self.control = self.eval_value

    def eval_kontinuation(self):
        self.kontinuation[0]()

    # Always the last item in the kontinuation
    # Signals the end of an expression
    # Ends execution
    def c_empty(self):
        if self.return_val is None:
            self.return_val = self.values

        self.control = None
        return

    # Used after certain expressions to reset the environment
    # This emulates local environments for functions and let expressions
    def c_reset_env(self):
        for k, v in self.kontinuation[1].items():
            if v == tokens.pylsyntax.PylSyntax.sNil:
                del self.env[k]
            else:
                self.env[k] = v
        self.env.update(self.kontinuation[1])
        self.kontinuation = self.kontinuation[2]
        return

    # The first step in evaluating a function
    # Evaluates all the arguments first to ensure that only a single value
    # is passed to the function as opposed to an expression
    def c_proc_func(self):
        func = self.values
        args = self.kontinuation[1]
        k = self.kontinuation[2]

        self.list_exprs = args
        self.kontinuation = [self.c_proc_args, func, k]
        self.control = self.eval_map_value
        return

    # After the arguments are evaluated the function is then set up to be
    # run by the evalProcedure function
    def c_proc_args(self):
        args = self.values
        func = copy(self.kontinuation[1])
        keys = self.kontinuation[2]

        self.func = func
        self.args = args
        self.kontinuation = keys
        self.control = self.eval_procedure
        return

    # A step in evaluating more than one expression
    # Takes the first item returned puts it in a kontinuation then goes on
    # to evaluate the second argument
    def c_map_value_of_step(self):
        first = self.values
        second = self.kontinuation[1]
        k = self.kontinuation[2]

        self.list_exprs = second
        self.kontinuation = [self.c_map_value_of_cons, first, k]
        self.control = self.eval_map_value
        return

    # After cMapValueOfStep has been performed and the second value does not exist anymore
    # The first and second elements are then bound together in a Lst
    def c_map_value_of_cons(self):
        first = self.kontinuation[1]
        second = self.values
        k = self.kontinuation[2]

        self.kontinuation = k

        # Make sure that a proper Lst is returned
        if not isinstance(second, list):
            self.values = [first, second]
        elif len(second) > 0:
            self.values = [first] + second
        else:
            self.values = [first]

        self.control = self.eval_kontinuation
        return

    def eval_map_value(self):
        """
        Evaluates multiple values in a Lst.
        Works by evaluating the first element, then returning a list with all the rest. This continues until the second list is empty.
        """
        if self.list_exprs is None or len(self.list_exprs) == 0:
            self.values = self.list_exprs
            self.control = self.eval_kontinuation
            return

        else:
            self.expr = self.list_exprs[0]
            self.kontinuation = [self.c_map_value_of_step,
                                    self.list_exprs[1:], self.kontinuation]
            self.control = self.eval_value
            return

    def eval_procedure(self):
        """
        Evaluates a function. Makes a distinction between PyLisp functions, builtins, and partials
        """

        # Handle () as an argument
        if len([y for y in filter(lambda x: x is not None, self.args)]) == 0:
            self.args = []

        # A function defined in PyLisp
        if isinstance(self.func, tokens.function.Function):
            self.expr = self.func.expr

            # If the arguments are equal then evalute the function
            if len(self.args) == len(self.func.args):
                env = self.func.get_env(*self.args)
                init = {}
                for k in env.keys():
                    init[k] = self.env.get(k)
                self.env.update(env)
                self.kontinuation = [self.c_reset_env, init,
                                        self.kontinuation]
                self.control = self.eval_value

            # If it's more than, return an error
            elif len(self.args) > len(self.func.args):
                raise errors.syntaxerror.PylispSyntaxError(
                    "function {}".format(self.func.value),
                    "Too many arguments")

            # Otherwise, curry the function by setting some of the arguments
            else:
                func = deepcopy(self.func)
                func.env.update(func.get_env(*self.args))
                func.args = func.args[len(self.args):]
                self.values = func
                self.control = self.eval_kontinuation

            return

        elif isinstance(self.func, tokens.function.Builtin):
            self.control = self.eval_kontinuation

            if len(self.args) == self.func.arg_len or (
                self.func.has_unpack_args and len(self.args) >
                self.func.arg_len):
                try:
                    self.values = self.func(*self.args)
                except TypeError:
                    print(self.args)
                    raise errors.pylisptypeerror.PylispTypeError(
                        self.func, *self.args,
                        msg=" due to type mismatch")

            elif len(self.args) > self.func.arg_len:
                raise errors.syntaxerror.PylispSyntaxError(
                    "function {}".format(self.func), "Too many arguments")
            else:
                self.values = self.func
                self.values.args += tuple(self.args)
                self.values.arg_len -= 1

        elif len(self.args) > 0:
            raise errors.pylisptypeerror.PylispTypeError(
                self.func, *self.args,
                msg=" because {} is not a function".format(self.func))
        # Just a single token
        else:
            self.values = self.func
            self.control = self.eval_kontinuation

    def evaluate(self, expr):
        """
        Main loop. Sets the proper variables, then runs self.control until it is None, then returns the returnVal register
        """
        self.expr = expr
        self.kontinuation = [self.c_empty]
        self.control = self.eval_value
        self.return_val = None
        while self.control is not None:
            self.control()
        return self.return_val
