from env import Env
from interpreter.read import READ
from virtualmachine import VirtualMachine
from errors.pylisperror import PylispError


class FileParser():

    """
    FileParser is provided a filename and will then proceed to read the file and run each segment of code
    """

    def __init__(self, toRead):
        """
        Initliases the virtual machine and environment at the start
        """
        self.env = Env()
        self.env.setToStandardEnv()
        self.vm = VirtualMachine(self.env)
        self.toRead = toRead

    def parseFile(self):
        """
        The file is parsed by keeping count of all opening and closing parenthesis and then reading a character at a time.
        Once the opening parenthesis and closing parenthesis match each other, and are more than 0, a buffer is completed and added to the buffers list.
        """
        buffers = []
        # The line count is kept track of for error purposes
        lineCounter = 1
        with open(self.toRead, "r", encoding="utf-8") as f:
            currentBuffer = ""
            leftParens = 0
            rightParens = 0
            c = f.read(1)
            while c:
                # Ignore comments
                if c == ";":
                    while c:
                        if c == "\n" or c == "\r":
                            break
                        c = f.read(1)
                elif c == "(":
                    leftParens += 1
                elif c == ")":
                    rightParens += 1

                currentBuffer += c

                # Handle the end of an expression
                if leftParens == rightParens and leftParens > 0:
                    # currentBuffer = currentBuffer.replace("\n", "")
                    # currentBuffer = currentBuffer.replace("\r", "")
                    # Remove trailing newlines and spaces
                    currentBuffer = currentBuffer.strip()
                    buffers.append((currentBuffer, lineCounter))

                    # Reset the variables
                    currentBuffer = ""
                    leftParens = 0
                    rightParens = 0

                # Line count incrementing
                if c == "\n" or c == "\r":
                    lineCounter += 1

                c = f.read(1)

        return buffers

    def run(self):
        """
        The program is run by getting every buffer and linecount from parseFile then attempting the evaluate each buffer
        If it fails with a PylispError, the error and line number is returned
        """
        for i, k in self.parseFile():
            try:
                self.vm.EVAL(READ(i))
            except PylispError as e:
                print(e, "at line", k)
                return
