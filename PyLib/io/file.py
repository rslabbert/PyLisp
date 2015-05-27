from tokens.function import Builtin

def slurp(to_read):
    with open(to_read, "rU") as f:
        return [x.strip() for x in f.readlines()]

export = {
    "open-output-file": Builtin("open-output-file", lambda x: open(x, "rU")),
    "open-input-file": Builtin("open-input-file", lambda x: open(x, "wU")),
    "close-file": Builtin("close-file", lambda x: x.close()),
    "read": Builtin("read", lambda x: x.read()),
    "slurp": Builtin("slurp", slurp)
}
