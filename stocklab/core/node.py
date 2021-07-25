from . import StocklabObject
from .config import get_config
from .runtime import Surrogate
from .crawler import CrawlerTrigger

class Node(StocklabObject):
    def __init__(self):
        super().__init__()
        if hasattr(type(self), 'crawler_entry') and \
                isinstance(type(self).crawler_entry, Surrogate):
            type(self).crawler_entry = Surrogate.resolve(type(self).crawler_entry)
        # TODO: perform checks on configs
        # TODO: perform checks on individual configs

    def default_attr(self, attr, default_val):
        if not hasattr(self, attr):
            setattr(self, attr, default_val)

    def path(self, **kwargs):
        return '.'.join([self.name] + [
            f'{k}:{v}' for k, v in kwargs.items() if k != 'self'])

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
        try:
            return type(self).evaluate(**kwargs)
        except CrawlerTrigger as t:
            return type(self).crawler_entry(**t.kwargs)

    def evaluate(**kwargs):
        raise NotImplementedError()

class Arg(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: setattr if oneof is set
        if 'type' not in self:
            self['type'] = str

Args = dict
