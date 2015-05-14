from tokens.function import Builtin

# File containing io related functions, can be imported into the environment using import io
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
export = {
    "newline": Builtin("newline", lambda: print("")),
    "display": Builtin("display", lambda x: print(x,
                                                  end="",
                                                  sep="")),
    "displayln": Builtin("displayln", lambda x: print(x, sep=""))
}
