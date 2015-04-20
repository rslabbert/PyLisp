# PyLisp

## TODO
* Make library use resetEnv with initials properly instead of deepcopy env
* Make some of the standard library be in pylisp
* Make optimisations
    * Potentially using flags -O -O2 etc.
    * Can speed up enums https://github.com/ze-phyr-us/fastenum
* Think about implementing an IO type to make the language more pure
* Write more tests
* Implement almost the entire scheme standard
* Start work on a standard library

## Usage
To run pylisp you can execute the `bin/pylisp` shell file, assuming sh/bash/zsh/etc. is installed, otherwise running python3 main.py works too.
If pylisp is run without any arguments it starts an interpreter session, if run with an argument it attempts to open it as a file.

Inside the interpreter pressing tab will attempt to complete any variable names or core syntactic keywords, and entering a newline while there are more opening parenthesis than closing parenthesis will result in an indent newline that accepts input, allowing multi-line expressions.
