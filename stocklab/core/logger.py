import logging

from .config import is_configured, get_config

__global_logger = None
__loggers = {}

def _create(name, level):
    logger = logging.getLogger(name)
    log_handler = logging.StreamHandler()
    if name == 'stocklab':
        fmt = f"[%(levelname)s] %(message)s"
    else:
        fmt = f"[%(levelname)s] ({name}) : %(message)s"
    log_format = logging.Formatter(fmt)
    log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)
    logger.setLevel(getattr(logging, level))
    return logger

def get_instance(name=None):
    """
    Returns the logger if it exists, otherwise setup a logger with stocklab
    logging format.  Since the configuration specifies the log level,
    stocklab must be configured before getting a logger.
    
    :param name: The name of the logger, defaults to None.
    :type name: str
    :returns: logging.Logger
    """
    global __loggers, __global_logger
    if name and name != 'stocklab': # 'stocklab' is reserved for global logger
        if name not in __loggers:
            assert is_configured(), 'Stocklab must be configured ' \
                    'before this routine can be called.'
            __loggers[name] = _create(name, get_config('log_level'))
        return __loggers[name]
    else:
        if not __global_logger:
            level = get_config('log_level') if is_configured() else 'DEBUG'
            __global_logger = _create('stocklab', level)
        return __global_logger
