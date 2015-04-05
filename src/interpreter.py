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

        self.intro = "Welcome to the PyLisp interpreter"

        # Sets the global variable environment to the standard set
        self.replEnv = Env()
        self.replEnv.setToStandardEnv()

        self.vm = VirtualMachine(self.replEnv)

        # Uses the readline library to gain tab completion, matching
        # parenthesis, and automatic history
        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set blink-matching-paren on')

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
        promptIndent = len(self.prompt) - len("...")
        while ret.count("(") > ret.count(")"):
            indent = (ret.count("(") - ret.count(")")) * 2
            ret += " " + \
                input("\r" + " " * promptIndent + "..." + indent * " ")

        return ret

    def cmdloop(self):
        """
        The main loop. Gets the input, sends it to precmd, then runs it. If it encounters a pylisp error, prints the error and cleans up.
        If it enconters an EOF i.e. Ctrl-D it closes gracefully
        """
        print(self.intro)
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
