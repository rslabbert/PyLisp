import os
from inspect import getfile
from importlib.machinery import SourceFileLoader

import errors.librarynotfound
import errors.libraryerror
from tokens.pylsyntax import PylSyntax


class Env(dict):
    """
    The environment which is used to find variables and symbols and their associated value
    """

    def __init__(self, secondary_env=None):
        """
        secEnv variable to allow an environment to inherit from a previous one
        """
        # Beware mutable default args
        if not secondary_env:
            secondary_env = {}
            
        dict.__init__(self)
        self.update(secondary_env)

        # The standard library will be in PyLisp/PyLib
        self.std_path = os.path.join(
            os.path.dirname(os.path.dirname(getfile(Env))), "PyLib")
        self.std_libs = {}
        self.get_libs()
        self.standard_env = ["core"]

    def get_libs(self):
        """
        Gets all the libraries in the std path and adds it to the std_libs variable
        """
        for dirs in os.listdir(self.std_path):
            if os.path.isdir(os.path.join(self.std_path, dirs)) and not dirs.startswith("__"):
                self.std_libs.update({os.path.basename(dirs): os.path.join(self.std_path, dirs)})

    def get_lib(self, path):
        """
        Gets all the python and pylisp files associated with a library amd returns it in a list
        """
        return_list = [] 
        for root, dirs, files in os.walk(path):
            for i in files:
                if i.endswith(".py") and not i.endswith("__init__.py"):
                    return_list.append(os.path.join(root, i).replace(self.std_path + "/", ""))
                elif i.endswith(".pyl"):
                    return_list.append(os.path.join(root, i))

        return return_list

    def include_lib(self, lib):
        """
        Loops through the files for a library and imports each one
        """
        path = self.std_libs.get(lib)
        if path is None:
            raise errors.librarynotfound.LibraryNotFound(lib)
        else:
            ret = []
            for val in self.get_lib(path):
                # If it is a python file evaluate it and check for the module.export variable
                if val.endswith(".py"):
                    pf = SourceFileLoader(lib, os.path.join(self.std_path, val))
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

    def set(self, keys, vals):
        """
        Convenience function for self.update which accepts a range of keys and values. If a single key, value is given, it is then returned after being inserted
        """
        if isinstance(keys, list):
            for i, k in enumerate(keys):
                self.update({k: vals[i]})
            return
        else:
            self.update({keys: vals})
            return vals

    def get(self, key, default=PylSyntax.sNil):
        """
        Just overrides the default env get with a default default
        """
        return dict.get(self, key, default)
