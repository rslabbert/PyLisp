from collections import ChainMap
from os import name as osname
from os import environ
from os.path import expanduser, join

import env
from pylparser import Parser
from virtualmachine import VirtualMachine
from fileparser import FileParser
from errors.pylisperror import PylispError


class Interpreter():
    """
    A read eval print loop interactive interpreter. Takes input from the user and displays the resultant output on the next line
    """

    def __init__(self):
        
        # Windows does not have GNU readline, and has different environment variables
        if osname == 'nt':
            username = environ["USERNAME"]
        else:
            import readline
            import atexit
            username = environ["USER"]
            
            # Uses the readline library to gain tab completion, matching
            # parenthesis, and automatic history
            readline.set_completer(self.complete)
            readline.parse_and_bind('tab: complete')
            readline.parse_and_bind('set blink-matching-paren on')
    
            self.histfile = join(expanduser("~"), ".pylisp_history")
            try:
                readline.read_history_file(self.histfile)
            except FileNotFoundError:
                open(self.histfile, 'a').close()
    
            self.completion_candidates = []
    
            atexit.register(readline.write_history_file, self.histfile)
            
        # Initialises using the user's username as the prompt
        self.prompt = username + "> "

        self.intro = "Welcome to the PyLisp interpreter"

        self.vm = VirtualMachine(ChainMap())
        self.load_std()
        self.registers = None
        
    def load_std(self):
        """
        Adds the core libraries to the environment
        """
        for i in env.standard_env:
            libs = env.include_lib(i)
            for lib in libs:
                if lib[0] == "py":
                    self.vm.env.update(lib[1])
                elif lib[0] == "pyl":
                    file_parse = FileParser(lib[1], self.vm)
                    file_parse.run()

    def complete(self, text, state):
        """
        The completer function. Works by finding all the symbols in the environment and in the core keywords and checking if they start with the provided text
        """
        if state == 0:
            self.completion_candidates = []

            tmp = []
            tmp.extend(self.repl_env.keys())
            tmp.extend(self.vm.core_keywords.keys())

            for i in tmp:
                if i.startswith(text):
                    self.completion_candidates.append(i)

        if state < len(self.completion_candidates):
            result = self.completion_candidates[state]
        else:
            result = None

        return result

    def precmd(self, line):
        """
        Executed on the input before the line is evaluated. Used to ensure that if the opening brackets do not match the closing brackets, the prompt is just extended
        """
        ret = line
        prompt_indent = len(self.prompt) - len("...")
        while ret.count("(") > ret.count(")"):
            indent = (ret.count("(") - ret.count(")")) * 2
            ret += " " + \
                input("\r" + " " * prompt_indent + "..." + indent * " ")

        return ret

    def cmdloop(self):
        """
        The main loop. Gets the input, sends it to precmd, then runs it. If it encounters a pylisp error, prints the error and cleans up.
        If it enconters an EOF i.e. Ctrl-D it closes gracefully
        """
        print(self.intro)
        while True:
            self.registers = self.vm.get_registers()
            try:
                inp = input(self.prompt)
                inp = self.precmd(inp)

                parser = Parser()
                print(self.vm.evaluate(parser.parse_buffer(inp)))

            except PylispError as e:
                print(e)
                self.vm.set_registers(self.registers)
            except (KeyboardInterrupt, EOFError):
                return
