import sys

from . import bundle

class Surrogate:
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
