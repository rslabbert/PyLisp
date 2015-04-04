# File containing io related functions, can be imported into the environment using import io
# Lambdas are used instead of builtin functions since the argument count
# can then be accessed which is used for currying
io = {
    "newline": lambda: print(""),
    "display": lambda x: print(x, end="", sep="")
}
