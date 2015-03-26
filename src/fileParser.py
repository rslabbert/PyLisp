from env import Env
from interpreter.read import READ
from virtualmachine import VirtualMachine


class FileParser():
    """Docstring for FileReader. """
    def __init__(self, toRead):
        self.env = Env()
        self.env.setToStandardEnv()
        self.vm = VirtualMachine(self.env)
        self.toRead = toRead

    def parseFile(self):
        buffers = []
        lineCounter = 1
        with open(self.toRead, "r", encoding="utf-8") as f:
            currentBuffer = ""
            leftParens = 0
            rightParens = 0
            c = f.read(1)
            while c:
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

                if leftParens == rightParens and leftParens > 0:
                    currentBuffer = currentBuffer.replace("\n", "")
                    currentBuffer = currentBuffer.replace("\r", "")
                    buffers.append((currentBuffer, lineCounter))
                    currentBuffer = ""
                    leftParens = 0
                    rightParens = 0

                if c == "\n" or c == "\r":
                    lineCounter += 1

                c = f.read(1)

        return buffers

    def run(self):
        for i, k in self.parseFile():
            print(k, i)
            self.vm.EVAL(READ(i))


if __name__ == '__main__':
    parser = FileParser("tests/simpleFile.pyl")
    parser.parseFile()
