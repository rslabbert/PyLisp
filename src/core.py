import tokens
from env import Env


coreKeywords = ["define", "lambda", "let", "do", "if", "set!", "display"]


def do_define(expr1, expr2, EVAL, env):
    if isinstance(expr1, list):
        # Defining Function
        return env.set(expr1[0].value, do_lambda(expr1[1:], expr2, env))
    else:
        # Defining variable
        return env.set(expr1.value, EVAL(expr2, env))


def do_lambda(args, expr, env):
    if expr is None:
        return tokens.function.Function([], args, env)
    return tokens.function.Function(args, expr, env)


def do_let(assigns, expr, EVAL, env):
    letEnv = Env(env)
    for i in assigns:
        letEnv.set(i[0].value, EVAL(i[1], letEnv))
    return expr, letEnv


def do_if(condition, true, false, EVAL, env):
    return true if EVAL(condition, env) else (false if false is not None else tokens.nil.Nil())


def do_do(exprs, EVAL, env):
    return [EVAL(x, env) for x in exprs][-1]


def do_set(name, val, EVAL, env):
    return env.set(name.value, EVAL(val, env)) if name.value in env.keys() else "No wrok"


def do_library(name, env, args):
    return env.set(name, args)


def do_import(name, EVAL, env):
    inp, env = [EVAL(x, env) for x in env.get(name)]
    return inp, env
