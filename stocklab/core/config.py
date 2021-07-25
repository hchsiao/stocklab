import os

__config = None

def is_configured():
    return __config is not None

def get_config(key):
    assert is_configured()
    return __config[key]

def configure(config):
    """ Read the configurations and initialize a logger
        for stocklab at the runtime.  Config 'root_dir' will be
        normalized to an absolute path.
    
    :param config: Could be the path to the configuration yaml file, or a
        `dict` loaded with that content.
    :type config: str, dict
    :raises NotImplementedError: Currently, only configuration by file
        is implemented.
    """
    global __config

    if os.path.isfile(config):
        from yaml import load, dump
        try:
            from yaml import CLoader as Loader, CDumper as Dumper
        except ImportError:
            from yaml import Loader, Dumper
        __config = load(open(config, 'r').read(), Loader=Loader)
        relative_path_base = os.path.dirname(os.path.realpath(config))
    else:
        assert type(config) is not str, f'File {config} cannot be opened.'
        relative_path_base = os.getcwd()
        raise NotImplementedError()

    assert type(__config) is dict
    if not os.path.isabs(__config['root_dir']):
        __config['root_dir'] = os.path.join(
                relative_path_base, __config['root_dir'])
    __config['root_dir'] = os.path.normpath(__config['root_dir'])

    import logging
    from . import logger
    logger.get_instance().setLevel(getattr(logging, __config['log_level']))
