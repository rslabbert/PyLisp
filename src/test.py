from env import Env
from virtualmachine import VirtualMachine
from interpreter.read import READ
from interpreter.printer import PRINT


def main():

    # Sets the global variable environment to the standard set
    env = Env()
    env.setToStandardEnv()
    vm = VirtualMachine(env)

    # Main loop which prompts user for input and print the response of the input handed to the rep function
    # inp = "(define (fac n) (if (= n 1) n (* n (fac (- n 1)))))"
    testList = ["(define r 10)",
                "r",
                "(if (= r 10) #t #f)",
                "(if (= r 9) #t #f)",
                "(if (= 9 9) #t #f)",
                "(if (= 8 9) #t #f)",
                "(define f (lambda (x) (+ x x)))",
                "(f 2)",
                "((lambda (x) (+ x x)) 2)",
                "(define fac (lambda (n) (if (= n 1) n (* n (fac (- n 1))))))",
                "(fac 5)",
                "(let ((x 2) (y 2)) (+ x y))"]

    # testList =

    offset = 0
    for inp in testList[offset:]:
        print(inp)
        PRINT(vm.EVAL(READ(inp)))

    print(env)


if __name__ == '__main__':
    main()
