from .core.bundle import bundle, register, get_node
from .core.config import configure

DataIdentifier = get_node

def eval(di_str):
    names = di_str.split('.')
    node_name = names[0]
    fields = [field.split(':') for field in names[1:]]
    fields = {k:v for k,v in fields}
    node = get_node(node_name)
    return node(**fields)
