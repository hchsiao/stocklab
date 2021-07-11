import os
import sys

from .core import bundle
from .core.runtime import Surrogate

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
