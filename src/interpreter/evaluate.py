import tokens
import core


def EVAL(inp, env):
    """Evaluates and runs the input parsed by the user"""
    while True:
        # Checks whether the input is a list and if not handles all the single input cases
        if not isinstance(inp, tokens.lst.Lst):
            if isinstance(inp, tokens.symbol.Symbol):
                return env.get(inp.value)
            elif isinstance(inp, tokens.string.String):
                return inp.value
            elif isinstance(inp, tokens.number.Number):
                try:
                    return int(inp.value)
                except ValueError:
                    return float(inp.value)
            elif isinstance(inp, tokens.nil.Nil):
                return "nil"
            elif isinstance(inp, tokens.lst.Lst):
                return [EVAL(x, env) for x in inp]
            else:
                return inp

        # If it is a list:
        if len(inp) == 0:
            return inp

        sym = inp[0]

        # If the first item is a list, then that is evaluated
        if isinstance(sym, list):
            inp = sym
            continue

        # Otherwise, it checks for language level features

        if sym.value == "debug":
            return env
        # define creates a variable in the current environment
        elif sym.value == "define":
            return core.do_define(inp[1], inp[2], EVAL, env)
        # Sets a variable which already exists to a new value
        elif sym.value == "set!":
            return core.do_set(inp[1], inp[2], EVAL, env)
        # let sequentially sets all the variables in the first argument into an env and uses it the evaluate the second argument
        elif sym.value == "let":
            inp, env = core.do_let(inp[1], inp[2], EVAL, env)
        # if evaluates a condition and if true returns the 3rd argument, and if false returns the 4th. If the 4th argument is missing, it returns nil
        elif sym.value == "if":
            inp = core.do_if(inp[1], inp[2], inp[3], EVAL, env)
        # Defines an anonymous function which is not added to the environment
        elif sym.value == "lambda":
            return core.do_lambda(inp[1], inp[2], env)
        # Evaluate all the expressions and return the value of the last one
        elif sym.value == "do":
            return core.do_do(inp[1], EVAL, env)
        elif sym.value == "library":
            return core.do_library(inp[1][0].value, env, inp[2:])
        elif sym.value == "import":
            inp, env = core.do_import(inp[1].value, EVAL, env)
        # Prints the argument
        elif sym.value == "print":
            print(EVAL(inp[1], env))
            return
        else:
            # if not a language level feature, it evaluates the symbol as a function and passes what's after it as arguments. The arguments are evaluated first
            # TODO implement tail call optimization
            func = env.get(sym.value)
            args = [EVAL(x, env) for x in inp[1:]]

            if isinstance(func, tokens.function.Function):
                inp, env = func(*args)
            else:
                return func(*args)
