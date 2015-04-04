import readline
from os import environ

from env import Env
from parser import Parser
from virtualmachine import VirtualMachine, coreKeywords
from errors.pylisperror import PylispError


class Interpreter():

    """
    A read eval print loop interactive interpreter. Takes input from the user and displays the resultant output on the next line
    """

    def __init__(self):
        # Initialises using the environment as the prompt
        username = environ["USER"]
        self.prompt = username + "> "

        # Promptindent and indent variables are useful for subshells, to align
        # brackets properly
        self.promptIndent = len(self.prompt) - 2
        self.indent = 0

        self.intro = "Welcome to the PyLisp interpreter"

        # Sets the global variable environment to the standard set
        self.replEnv = Env()
        self.replEnv.setToStandardEnv()

        self.vm = VirtualMachine(self.replEnv)

        # Uses the readline library to gain tab completion, matchin
        # parenthesis, and automatic history
        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set blink-matching-paren on')

        # Automatically insert closing brackets after typing opening one
        # http://stackoverflow.com/questions/11486757/autoclose-gnu-readline
        readline.parse_and_bind('"(" "\C-v()\e[D"')
        readline.parse_and_bind('"\"": "\C-v\"\C-v\"\e[D"')

        self.histfile = ".pylisp_history"
        try:
            readline.read_history_file(self.histfile)
        except FileNotFoundError:
            pass

        self.completionCandidates = []

    def complete(self, text, state):
        """
        The completer function. Works by finding all the symbols in the environment and in the core keywords and checking if they start with the provided text
        """
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
        """
        Executed on the input before the line is evaluated. Used to ensure that if the opening brackets do not match the closing brackets, the prompt is just extended
        """
        ret = line
        indent = (ret.count("(") - ret.count(")")) * 2
        while ret.count("(") > ret.count(")"):
            subSh = SubShell(self.promptIndent, self.indent + indent)
            ret += " " + subSh.cmdloop()
            self.indent = (ret.count("(") - ret.count(")")) * 2

        return ret

    def cmdloop(self):
        """
        The main loop. Gets the input, sends it to precmd, then runs it. If it encounters a pylisp error, prints the error and cleans up.
        If it enconters an EOF i.e. Ctrl-D it closes gracefully
        """
        while True:
            self.registers = self.vm.getRegisters()
            try:
                inp = input(self.prompt)
                inp = self.precmd(inp)

                parser = Parser()
                print(self.vm.EVAL(parser.parseBuffer(inp)))

            except PylispError as e:
                print(e)
                self.cleanUp()
            except EOFError:
                print("Bye")
                self.cleanUp()
                return

    def cleanUp(self):
        """
        Writes to history to the file and resets the registers
        """
        readline.write_history_file(self.histfile)
        self.vm.setRegisters(self.registers)


class SubShell(Interpreter):
    """
    Used for when the opening braces are more than the closing braces
    """
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
