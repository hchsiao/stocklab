import os

__config = None

def is_configured():
    return __config is not None

def get_config(key):
    assert is_configured()
    return __config[key]

def configure(config):
    """ Read the configurations and initialize a logger
        for stocklab at the runtime.
    
    :param config: Could be the path to the configuration
        yaml file, or a python dict with the same information.
    :returns: None
    :raises NotImplementedError: TODO
    """
    global __config

    if os.path.isfile(config):
        from yaml import load, dump
        try:
            from yaml import CLoader as Loader, CDumper as Dumper
        except ImportError:
            from yaml import Loader, Dumper
        __config = load(open(config, 'r').read(), Loader=Loader)
    else:
        raise NotImplementedError()

    from . import logger
    logger.get_singleton('stocklab')
