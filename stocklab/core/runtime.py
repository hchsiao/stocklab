import os
import sys

from . import bundle

class Surrogate:
    """
    To make stocklab objects be able to dynamically loaded and be able to
    import each other, all such classes will have a corresponding handle
    (i.e. the `Surrogate`) and can be imported by::

        from stocklab.core.runtime import MyNode

    Later in the node creation phase, we can lookup the actual class object
    of a `Surrogate` from stocklab bundles by::

        MyNode = Surrogate.resolve(MyNode)

    """
    @staticmethod
    def resolve(srg):
        dot_sep_path = srg.args
        obj = bundle._get(dot_sep_path[0], 'nodes', xcpt=False) or \
                bundle._get(dot_sep_path[0], 'crawlers', xcpt=False)
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
    """The customized import hook to import stocklab components."""
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
