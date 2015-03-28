import readline
import sys
from os import environ

from env import Env
from virtualmachine import VirtualMachine, coreKeywords
from interpreter.rep import rep
from errors.pylisperror import PylispError


class Interpreter():
    """Docstring for Interpreter. """
    def __init__(self):
        username = environ["USER"]
        self.prompt = username + "> "
        self.promptIndent = len(self.prompt) - 2
        self.indent = 0
        self.intro = "Welcome to the PyLisp interpreter"

        # Sets the global variable environment to the standard set
        self.replEnv = Env()
        self.replEnv.setToStandardEnv()

        self.vm = VirtualMachine(self.replEnv)
        self.registers = None

        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set blink-matching-paren on')

        self.histfile = ".pylisp_history"
        try:
            readline.read_history_file(self.histfile)
        except FileNotFoundError:
            pass

        self.completionCandidates = []

    def run(self, line):
        rep(line, self.vm)

    def complete(self, text, state):
        if state == 0:
            self.completionCandidates = []

            for i in list(self.replEnv.keys()) + coreKeywords:
                if i.startswith(text):
                    self.completionCandidates.append(i)

        if state < len(self.completionCandidates):
            result = self.completionCandidates[state]
        else:
            result = None

        return result

    def precmd(self, line):
        ret = line
        indent = (ret.count("(") - ret.count(")")) * 2
        while ret.count("(") > ret.count(")"):
            subSh = SubShell(self.promptIndent, self.indent + indent)
            ret += " " + subSh.cmdloop()
            self.indent = (ret.count("(") - ret.count(")")) * 2

        return ret

    def cmdloop(self):
        self.registers = self.vm.getRegisters()
        while True:
            try:
                inp = input(self.prompt)
                inp = self.precmd(inp)
                self.run(inp)
            except PylispError as e:
                print(e)
            except EOFError:
                print("Bye")
                self.cleanUp()
                return
            except:
                print("Unexpected error:", sys.exc_info()[0])
                self.cleanUp()
                return

    def cleanUp(self):
        readline.write_history_file(self.histfile)
        self.vm.setRegisters(self.registers)


class SubShell(Interpreter):
    """Docstring for SubShell. """
    def __init__(self, promptIndent, indent):
        Interpreter.__init__(self)
        self.intro = ""
        self.promptIndent = promptIndent
        self.indent = indent
        self.prompt = promptIndent * " " + ">" + indent * " "

    def cmdloop(self):
        inp = input(self.prompt)
        inp = self.precmd(inp)
        return inp
