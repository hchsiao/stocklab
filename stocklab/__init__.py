from .core.bundle import bundle, register, get_node
from .core.config import configure

DataIdentifier = get_node

def reset():
    from .core.config import _reset as reset_config
    from .core.bundle import _reset as reset_bundle
    from .core.logger import _reset as reset_logger
    reset_config()
    reset_bundle()
    reset_logger()

def eval(di_str):
    """
    Evaluate the DataIdentifier string.

    :param di_str: the DataIdentifier.
    :type di_str: str
    """
    names = di_str.split('.')
    node_name = names[0]
    fields = [field.split(':') for field in names[1:]]
    fields = {k:v for k,v in fields}
    node = get_node(node_name)
    return node(**fields)
