from parser import Parser
from errors.pylisperror import PylispError
from errors.filenotfound import PylispFileNotFoundError
import os


class FileParser():
    """
    FileParser is provided a filename and will then proceed to read the file and run each segment of code
    """

    def __init__(self, to_read, vm):
        """
        Initliases the virtual machine and environment at the start
        """
        self.vm = vm
        self.to_read = os.path.abspath(to_read)

        if not os.path.exists(self.to_read):
            raise PylispFileNotFoundError(self.to_read)

        os.chdir(os.path.dirname(self.to_read))


    def load_std(self):
        to_read = self.to_read
        for i in self.vm.env.standard_env:
            libs = self.vm.env.include_lib(i)
            for lib in libs:
                if lib[0] == "py":
                    self.vm.env.update(lib[1])
                elif lib[0] == "pyl":
                    self.to_read = lib[1]
                    os.chdir(os.path.dirname(self.to_read))
                    self.run()

        self.to_read = to_read
        os.chdir(os.path.dirname(self.to_read))

    def parse_file(self):
        """
        The file is parsed by keeping count of all opening and closing parenthesis and then reading a character at a time.
        Once the opening parenthesis and closing parenthesis match each other, and are more than 0, a buffer is completed and added to the buffers list.
        """
        buffers = []
        # The line count is kept track of for error purposes
        line_counter = 1
        with open(self.to_read, "rU", encoding="utf-8") as f:
            current_buffer = ""
            left_parens = 0
            right_parens = 0
            c = f.read(1)
            while c:
                # Ignore comments
                if c == ";":
                    while c:
                        if c == "\n":
                            break
                        c = f.read(1)
                elif c == "(":
                    left_parens += 1
                elif c == ")":
                    right_parens += 1

                current_buffer += c

                # Handle the end of an expression
                if left_parens == right_parens and left_parens > 0:
                    # Remove trailing newlines and spaces
                    current_buffer = current_buffer.strip()
                    buffers.append((current_buffer, line_counter))

                    # Reset the variables
                    current_buffer = ""
                    left_parens = 0
                    right_parens = 0

                # Line count incrementing
                if c == "\n":
                    line_counter += 1

                c = f.read(1)

        return buffers

    def run(self):
        """
        The program is run by getting every buffer and linecount from parseFile then attempting the evaluate each buffer
        If it fails with a PylispError, the error and line number is returned
        """
        for i, k in self.parse_file():
            try:
                parser = Parser()
                self.vm.evaluate(parser.parse_buffer(i))
            except PylispError as e:
                print(os.path.basename(self.to_read) + ":", e, "at line", k)
                return
