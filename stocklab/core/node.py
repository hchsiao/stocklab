from . import StocklabObject
from ..runtime import Surrogate

class Node(StocklabObject):
    def __init__(self):
        super().__init__()
        if isinstance(self.crawler_entry, Surrogate):
            self.crawler_entry = Surrogate.resolve(self.crawler_entry)
        # TODO: perform checks on configs
        # TODO: perform checks on individual configs

    def __call__(self, **kwargs):
        assert len(self.args) == len(kwargs), f'Invalid fields: {kwargs}'
        assert all([k in self.args for k in kwargs.keys()]), f'Invalid fields: {kwargs}'
        type_correct_fields = {k:self.args[k]['type'](v) for k, v in kwargs.items()}
        type_correct_fields['self'] = self # Call-style adaption
        retval = self.evaluate(**type_correct_fields)
        assert retval is not None # TODO: do more sophiscated check
        return retval

    def evaluate(self, **kwargs):
        raise NotImplementedError()

class Arg(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: setattr if oneof is set
        if 'type' not in self:
            self['type'] = str

Args = dict
Schema = dict
