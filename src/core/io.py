from functools import partial

io = {
    "newline": partial(print, ""),
    "display": partial(print, end="", sep="")
}
