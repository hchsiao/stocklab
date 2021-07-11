from .logger import get_singleton as get_logger

class SingletonType(type):
    def __init__(cls, name, base, dict):
        super().__init__(name, base, dict)
        cls._singleton = None

    def __call__(cls):
        """ The __call__ is overridden to make the class singletons. """
        if cls._singleton is None:
            print(f'New singleton for {cls.__name__} created')
            cls._singleton = super().__call__()
        return cls._singleton

class StocklabObjectType(SingletonType):
    def __init__(cls, name, base, dict):
        super().__init__(name, base, dict)
        cls._config = {k:v for k, v in dict.items() if k[0] != '_'}

class StocklabObject(metaclass=StocklabObjectType):
    def __init__(self):
        self.logger = get_logger(self.name)
        for k, v in type(self)._config.items():
            setattr(self, k, v)

    @property
    def name(self):
        return type(self).__name__
