import os
import sys

from .core import bundle

class Surrogate:
    @staticmethod
    def resolve(srg):
        dot_sep_path = srg.args
        obj = bundle.get_node(dot_sep_path[0]) or \
                bundle.get_crawler(dot_sep_path[0])
        for n in dot_sep_path[1:]:
            obj = getattr(obj, n)
        return obj

    def __init__(self, *args):
        self.args = args

    def __getattr__(self, attr):
        new_args = list(self.args) + [str(attr)]
        return Surrogate(*new_args)

    def __getitem__(self, key):
        raise NotImplementedError()

    def __str__(self):
        return '.'.join(self.args)

    def __repr__(self):
        return self.__str__()

class StocklabRuntimeImporter:
    objs = []
    def find_module(self, module_name, package_path):
        if module_name in StocklabRuntimeImporter.objs:
            return self
        else:
            return None

    def load_module(self, module_name):
        sys.modules[module_name] = Surrogate(module_name)

sys.meta_path.append(StocklabRuntimeImporter())

for bndl in bundle.__bundles:
    for fp in bndl['files']:
        fbase = os.path.basename(fp)
        fname, fext = os.path.splitext(fbase)
        StocklabRuntimeImporter.objs.append(fname)
        exec(f'import {fname}')
