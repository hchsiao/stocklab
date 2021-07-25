import logging

from .config import is_configured, get_config

__loggers = {}

def get_instance(name):
    """ Returns the logger if it exists, otherwise setup a
        logger with stocklab logging format.  Since the
        configuration specifies the log level, stocklab must
        be configured before getting a logger.
    
    :param name: A string represents the name of the logger.
    :returns: A logger.
    """
    global __loggers
    if name in __loggers:
        return __loggers[name]
    else:
        assert is_configured(), 'Stocklab must be configured ' \
                'before this routine can be called.'
        logger = logging.getLogger(name)
        log_handler = logging.StreamHandler()
        log_format = logging.Formatter(
                f"[%(levelname)s] {name}: %(message)s"
                )
        log_handler.setFormatter(log_format)
        logger.addHandler(log_handler)
        logger.setLevel(getattr(logging, get_config('log_level')))
        __loggers[name] = logger
        return logger
