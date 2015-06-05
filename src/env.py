import os
from inspect import getfile, currentframe
from importlib.machinery import SourceFileLoader

import errors.librarynotfound
import errors.libraryerror
from tokens.pylsyntax import PylSyntax


# The standard library will be in PyLisp/PyLib
std_path = os.path.join(
    os.path.dirname(os.path.dirname(getfile(currentframe()))), "PyLib")
std_libs = {}
standard_env = ["core"]

def get_libs():
    """
    Gets all the libraries in the std path and adds it to the std_libs variable
    """
    for dirs in os.listdir(std_path):
        if os.path.isdir(os.path.join(std_path, dirs)) and not dirs.startswith("__"):
            std_libs.update({os.path.basename(dirs): os.path.join(std_path, dirs)})

def get_lib(path):
    """
    Gets all the python and pylisp files associated with a library amd returns it in a list
    """
    return_list = [] 
    for root, dirs, files in os.walk(path):
        for i in files:
            if i.endswith(".py") and not i.endswith("__init__.py"):
                return_list.append(os.path.join(root, i).replace(std_path + "/", ""))
            elif i.endswith(".pyl"):
                return_list.append(os.path.join(root, i))

    return return_list

def include_lib(lib):
    """
    Loops through the files for a library and imports each one
    """
    path = std_libs.get(lib)
    if path is None:
        raise errors.librarynotfound.LibraryNotFound(lib)
    else:
        ret = []
        for val in get_lib(path):
            # If it is a python file evaluate it and check for the module.export variable
            if val.endswith(".py"):
                pf = SourceFileLoader(lib, os.path.join(std_path, val))
                try:
                    module = pf.load_module()
                    if hasattr(module, "export"):
                        ret.append(("py", module.export))
                    else:
                        ret.append(("None", "No Export"))
                except Exception as e:
                    raise errors.libraryerror.LibraryError(val, lib, e)
            # Pylisp files are just returned for the caller of the function to deal with
            elif val.endswith(".pyl"):
                ret.append(("pyl", val))

        return ret

get_libs()
