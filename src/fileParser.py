from env import Env
from interpreter.read import READ
from interpreter.virtualmachine import VirtualMachine


class FileParser():
    """Docstring for FileReader. """
    def __init__(self, toRead):
        self.env = Env()
        self.env.setToStandardEnv()
        self.toRead = toRead
        self.vm = VirtualMachine(self.env)

    def parseFile(self):
        buffers = []
        with open(self.toRead, "r", encoding="utf-8") as f:
            currentBuffer = ""
            leftParens = 0
            rightParens = 0
            c = f.read(1)
            while c:
                if c == "(":
                    leftParens += 1
                elif c == ")":
                    rightParens += 1

                currentBuffer += c

                if leftParens == rightParens and leftParens > 0:
                    buffers.append(currentBuffer.replace("\n", ""))
                    currentBuffer = ""
                    leftParens = 0
                    rightParens = 0
                c = f.read(1)

        return buffers

    def run(self):
        for i in self.parseFile():
            self.vm.EVAL(READ(i))


if __name__ == '__main__':
    parser = FileParser("tests/simpleFile.pyl")
    print(parser.parseFile())
