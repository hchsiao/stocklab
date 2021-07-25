from .logger import get_instance as get_logger

class SingletonType(type):
    """A singleton metaclass."""
    def __init__(cls, name, base, dict):
        super().__init__(name, base, dict)
        cls._singleton = None

    def __call__(cls):
        """The `__call__` is overridden to controll the instantiation."""
        if cls._singleton is None:
            cls._singleton = super().__call__()
        return cls._singleton

class StocklabObjectType(SingletonType):
    """
    Metaclass for stocklab objects.
    """
    def __init__(cls, name, base, dict):
        super().__init__(name, base, dict)
        cls._config = {k:v for k, v in dict.items() if k[0] != '_'}
        cls.name = cls.__name__

    def __getattr__(cls, name):
        return getattr(cls._singleton, name)

class StocklabObject(metaclass=StocklabObjectType):
    """
    Base class for the two main stocklab components: `Node` and `Crawler`.
    Its metaclass is `StocklabObjectType`.

    The object (i.e. singleton) of this type will share attributes between the
    class and the singleton.  A logger `self.logger` will be created for each
    singletons.
    """
    def __init__(self):
        self.logger = get_logger(self.name)
        for k, v in type(self)._config.items():
            setattr(self, k, v)

    def default_attr(self, attr, default_val):
        """Set `self.attr` to `default_val` if not already set."""
        if not hasattr(self, attr):
            setattr(self, attr, default_val)
