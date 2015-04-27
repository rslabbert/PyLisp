# PyLisp

## TODO
* Consider reimplementing map as a native function, since it gets really slow with large datasets
* Parse_cons isn't good, implement it using a macro expander or something
* Add a case structure
* Make library use resetEnv with initials properly instead of deepcopy env
* Make optimisations
    * Potentially using flags -O -O2 etc.
    * Can speed up enums https://github.com/ze-phyr-us/fastenum
* Think about implementing an IO type to make the language more pure
* Write more tests
* Implement almost the entire scheme standard
* Start work on a standard library
* Implement a macro expander system

## Usage
To run pylisp you can execute the `bin/pylisp` shell file, assuming sh/bash/zsh/etc. is installed, otherwise running python3 main.py works too.
If pylisp is run without any arguments it starts an interpreter session, if run with an argument it attempts to open it as a file.

Inside the interpreter pressing tab will attempt to complete any variable names or core syntactic keywords, and entering a newline while there are more opening parenthesis than closing parenthesis will result in an indent newline that accepts input, allowing multi-line expressions.
