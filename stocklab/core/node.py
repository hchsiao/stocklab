from . import StocklabObject
from .config import get_config
from .runtime import Surrogate
from .crawler import CrawlerTrigger

__cache = {}

def set_cache(key, val):
    global __cache
    __cache[key] = val

def get_cache(key):
    global __cache
    if key not in __cache:
        return None
    return __cache[key]

def flush_cache():
    global __cache
    __cache = {}

class Node(StocklabObject):
    """
    The base class for stocklab Nodes.  Nodes are callable, parameters are
    fields in the DataIdentifier.  It will return the evaluated result for a
    DataIdentifier.
    """
    def __init__(self):
        super().__init__()
        if hasattr(type(self), 'crawler_entry') and \
                isinstance(type(self).crawler_entry, Surrogate):
            type(self).crawler_entry = \
                    Surrogate.resolve(type(self).crawler_entry)
        # TODO: perform checks on configs
        # TODO: perform checks on individual configs

    def path(self, **kwargs):
        """
        :param kwargs: Fields.
        :returns: The DataIdentifier of the Fields with this node.
        """
        return '.'.join([self.name] + [
            f'{k}:{v}' for k, v in sorted(kwargs.items()) if k != 'self'])

    def type_normalization(self, kwargs):
        """
        Convert types for the fields according to the node's Args
        declaration.

        :returns: Checked & type casted parameters.
        """
        assert len(self.args) == len(kwargs), f'Invalid fields: {kwargs}'
        assert all([k in self.args for k in kwargs]), \
                f'Invalid fields: {kwargs}'
        for arg_name in kwargs:
            arg_type = self.args[arg_name].type
            arg_val = kwargs[arg_name]
            if type(arg_type) is type:
                kwargs[arg_name] = arg_type(arg_val)
            else: # Arg is enum
                assert type(arg_type) is list
                assert arg_val in arg_type
        return kwargs

    def __call__(self, **kwargs):
        kwargs = self.type_normalization(kwargs)
        path = self.path(**kwargs)
        if get_cache(path) is None:
            retval = self._resolve(**kwargs)
            assert retval is not None # TODO: do more sophiscated check
            set_cache(path, retval)
        return get_cache(path)

    def _resolve(self, **kwargs):
        try:
            return type(self).evaluate(**kwargs)
        except CrawlerTrigger as t:
            return type(self).crawler_entry(**t.kwargs)

    def evaluate(**kwargs):
        """
        This is used in the DataIdentifier evaluation. All child classes
        should implement their own evaluation function.
        """
        raise NotImplementedError()

class Arg(dict):
    """
    Used in node declarations. A `dict` of field specifications.
    :param type: TODO, defaults to `str`.
    :param oneof: (Optional) TODO.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'oneof' in self:
            self.type = self['oneof']
        else:
            self.type = self['type'] if 'type' in self else str

class Args(dict):
    """Used in node declarations. A `dict` of `Arg`."""
    pass
