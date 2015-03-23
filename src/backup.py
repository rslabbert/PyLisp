import tokens
from env import Env


def evalAtom(atom, env):
    if isinstance(atom, tokens.symbol.Symbol):
        return env.get(atom.value)
    elif isinstance(atom, tokens.string.String):
        return atom.value
    elif isinstance(atom, tokens.number.Number):
        return int(atom.value)
    elif isinstance(atom, tokens.nil.Nil):
        return "nil"
    elif isinstance(atom, list):
        return [evalAtom(x, env) for x in atom]
    else:
        return atom.value


def EVAL(inp, env):
    """Evaluates and runs the input parsed by the user"""
    while True:
        # Checks whether the input is a list and if not handles all the single input cases
        if not isinstance(inp, list):
            return evalAtom(inp, env)

        # If it is a list:
        if len(inp) == 0:
            return inp

        sym = inp[0]

        # If the first item is a list, then that is evaluated
        if isinstance(sym, list):
            inp = sym
            continue

        # Otherwise, it checks for language level features

        # define creates a variable in the current environment
        if sym.value == "define":
            if isinstance(inp[1], list):
                # Defining Function
                name = inp[1][0].value
                args = inp[1][1:]
                expr = inp[2]
                func = tokens.function.Function(args, expr, EVAL, env)
                return env.set(name, func)
            else:
                # Defining variable
                var = inp[1].value
                val = inp[2]
                return env.set(var, EVAL(val, env))
        # let* sequentially sets all the variables in the first argument into an env and uses it the evaluate the second argument
        elif sym.value == "let":
            var = inp[1]
            val = inp[2]
            letEnv = Env(env)
            for i in var:
                letEnv.set(i[0].value, EVAL(i[1], letEnv))
            inp = val
            env = letEnv
        # if evaluates a condition and if true returns the 3rd argument, and if false returns the 4th. If the 4th argument is missing, it returns nil
        elif sym.value == "if":
            condition = inp[1]
            true = inp[2]
            false = inp[3] if len(inp) > 3 else tokens.nil.Nil()
            result = (true if EVAL(condition, env) else false)
            inp = result
        # Defines an anonymous function which is not added to the environment
        elif sym.value == "lambda":
            args = inp[1]
            expr = inp[2]
            func = tokens.function.Function(args, expr, EVAL, env)
            return func
        # Evaluate all the expressions and return the value of the last one
        elif sym.value == "do":
            res = [EVAL(x, env) for x in inp[1]]
            return res[-1]
        # Prints the argument
        elif sym.value == "print":
            print(inp[1])
            return
        else:
            expr = evalAtom(inp, env)
            func = expr[0]

            # if not a language level feature, it evaluates the symbol as a function and passes what's after it as arguments. The arguments are evaluated first
            # func = env.get(sym.value)
            # args = [EVAL(x, env) for x in inp[1:]]

            if isinstance(func, tokens.function.Function):
                inp = func.expr
                env = func.getEnv(env, *expr[1:])
            else:
                return func(*expr[1:])
