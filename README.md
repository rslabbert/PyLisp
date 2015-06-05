# PyLisp

## Dependencies
* Python 3

## Usage
### OSX/Linux
Execute the `bin/pylisp.sh` file, or run `python3 src/main.py`.

### Windows
Execute the `bin/pylisp.bat` file, or run `src/main.py` through IDLE.

If pylisp is run without any arguments it starts an interpreter session, if run with an argument it attempts to open it as a file.

Inside the interpreter pressing tab will attempt to complete any variable names or core syntactic keywords, and entering a newline while there are more opening parenthesis than closing parenthesis will result in an indent newline that accepts input, allowing multi-line expressions.
