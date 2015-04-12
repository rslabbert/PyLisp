from parser import Parser
from errors.pylisperror import PylispError
import os


class FileParser():

    """
    FileParser is provided a filename and will then proceed to read the file and run each segment of code
    """

    def __init__(self, toRead, vm):
        """
        Initliases the virtual machine and environment at the start
        """
        self.vm = vm
        self.toRead = os.path.abspath(toRead)
        os.chdir(os.path.dirname(self.toRead))

    def parseFile(self):
        """
        The file is parsed by keeping count of all opening and closing parenthesis and then reading a character at a time.
        Once the opening parenthesis and closing parenthesis match each other, and are more than 0, a buffer is completed and added to the buffers list.
        """
        buffers = []
        # The line count is kept track of for error purposes
        lineCounter = 1
        with open(self.toRead, "rU", encoding="utf-8") as f:
            currentBuffer = ""
            leftParens = 0
            rightParens = 0
            c = f.read(1)
            while c:
                # Ignore comments
                if c == ";":
                    while c:
                        if c == "\n":
                            break
                        c = f.read(1)
                elif c == "(":
                    leftParens += 1
                elif c == ")":
                    rightParens += 1

                currentBuffer += c

                # Handle the end of an expression
                if leftParens == rightParens and leftParens > 0:
                    # Remove trailing newlines and spaces
                    currentBuffer = currentBuffer.strip()
                    buffers.append((currentBuffer, lineCounter))

                    # Reset the variables
                    currentBuffer = ""
                    leftParens = 0
                    rightParens = 0

                # Line count incrementing
                if c == "\n":
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
                parser = Parser()
                self.vm.EVAL(parser.parseBuffer(i))
            except PylispError as e:
                print(e, "at line", k)
                return
