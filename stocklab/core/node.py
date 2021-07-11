from . import StocklabObject
from .config import get_config
from .runtime import Surrogate

class Node(StocklabObject):
    def __init__(self):
        super().__init__()
        self.db = None
        if isinstance(self.crawler_entry, Surrogate):
            self.crawler_entry = Surrogate.resolve(self.crawler_entry)
        # TODO: perform checks on configs
        # TODO: perform checks on individual configs

    def type_normalization(self, kwargs):
        assert len(self.args) == len(kwargs), f'Invalid fields: {kwargs}'
        assert all([k in self.args for k in kwargs.keys()]), f'Invalid fields: {kwargs}'
        # TODO: do it 'inplace'
        type_correct_fields = {k:self.args[k]['type'](v) for k, v in kwargs.items()}
        return type_correct_fields

    def __call__(self, **kwargs):
        kwargs = self.type_normalization(kwargs)
        retval = self._resolve(**kwargs)
        assert retval is not None # TODO: do more sophiscated check
        return retval

    def _resolve(self, **kwargs):
        kwargs['self'] = self # Call-style adaption
        return self.evaluate(**kwargs)

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
