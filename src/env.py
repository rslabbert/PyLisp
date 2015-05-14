import os
from inspect import getfile
from importlib.machinery import SourceFileLoader

from tokens.pylsyntax import PylSyntax


class Env(dict):
    """
    The environment which is used to find variables and symbols and their associated value
    """

    def __init__(self, secondary_env=None):
        """
        secEnv variable to allow an environment to inherit from a previous one
        """
        if not secondary_env:
            secondary_env = {}
        dict.__init__(self)
        self.update(secondary_env)

        # The standard library will be in PyLisp/std
        self.std_path = os.path.join(
            os.path.dirname(os.path.dirname(getfile(Env))), "PyLib")
        self.std_libs = {}
        self.get_libs()
        self.standard_env = ["core"]

    def get_libs(self):
        for dirs in os.listdir(self.std_path):
            if os.path.isdir(os.path.join(self.std_path, dirs)) and not dirs.startswith("__"):
                self.std_libs.update({os.path.basename(dirs): os.path.join(self.std_path, dirs)})

    def get_lib(self, path):
        return_list = [] 
        for root, dirs, files in os.walk(path):
            for i in files:
                if i.endswith(".py") and not i.endswith("__init__.py"):
                    return_list.append(os.path.join(root, i).replace(self.std_path + "/", ""))
                elif i.endswith(".pyl"):
                    return_list.append(os.path.join(root, i))

        return return_list

    def include_lib(self, lib):
        path = self.std_libs.get(lib)
        if path is None:
            return []
        else:
            ret = []
            for val in self.get_lib(path):
                if val.endswith(".py"):
                    pf = SourceFileLoader(lib, os.path.join(self.std_path, val))
                    try:
                        module = pf.load_module()
                        if hasattr(module, "export"):
                            ret.append(("py", module.export))
                    except AttributeError:
                        ret.append(("None", "No Export"))
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
        return dict.get(self, key, default)
