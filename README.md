# PyLisp

## TODO
* Document everything with doc strings and comments
* Write more tests

## Dependencies
* Python 3

## Usage
To run pylisp, execute the `bin/pylisp` shell file, assuming `/bin/sh` is installed(which should be the case on unix system such as osx/linux), otherwise run `python3 src/main.py`.

If pylisp is run without any arguments it starts an interpreter session, if run with an argument it attempts to open it as a file.

Inside the interpreter pressing tab will attempt to complete any variable names or core syntactic keywords, and entering a newline while there are more opening parenthesis than closing parenthesis will result in an indent newline that accepts input, allowing multi-line expressions.
