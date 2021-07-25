from . import StocklabObject
from .config import get_config
from .runtime import Surrogate
from .crawler import CrawlerTrigger

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
            type(self).crawler_entry = Surrogate.resolve(type(self).crawler_entry)
        # TODO: perform checks on configs
        # TODO: perform checks on individual configs

    def path(self, **kwargs):
        """
        :param kwargs: Fields.
        :returns: The DataIdentifier of the Fields with this node.
        """
        return '.'.join([self.name] + [
            f'{k}:{v}' for k, v in kwargs.items() if k != 'self'])

    def type_normalization(self, kwargs):
        """
        Convert types for the fields according to the node's Args
        declaration.
        """
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
        """
        This is used in the DataIdentifier evaluation. All child classes
        should implement their own evaluation function.
        """
        raise NotImplementedError()

class Arg(dict):
    """Used in node declarations. A `dict` of field specifications."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: setattr if oneof is set
        if 'type' not in self:
            self['type'] = str

class Args(dict):
    """Used in node declarations. A `dict` of `Arg`."""
    pass
