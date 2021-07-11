""" This module handles the registration of nodes/crawlers
    and node/crawler collections (bundles).  A dict called
    `__bundle` contains the registrated nodes/crawlers.

bundle.__bundles: A list of bundles. Each bundle is a dict
    with four keys: 'base', 'files', 'nodes' and 'crawlers'.
    The default bundle is a dict with 'base' is None.  The
    value for 'files' is a list of source files.  The value
    of 'nodes' and 'crawlers' is a dict of (node/crawler
    name, class handle) pairs.  
"""
import os
import pathlib
import importlib.util

from .crawler import Crawler

__bundles = [
        {'base': None, 'files': [], 'nodes': {}, 'crawlers': {}}, # The default bundle
        ]

def bundle(bundle_path):
    """ Scan the bundle from a directory recursively and
        register them.
    
    :param bundle_path: The path to the bundle.
    :returns: None
    """
    global __bundles
    # Maintain the entry in __bundle
    if os.path.isfile(bundle_path):
        bundle_base = str(pathlib.Path(bundle_path).parent.resolve())
    else:
        bundle_base = bundle_path
    __bundles.append({'base': bundle_base, 'files': [], 'nodes': {}, 'crawlers': {}})
    curr_bundle = __bundles[-1]

    # Scan the bundle folder for nodes (file name ends with
    # .py) recurrsively
    def _scan(path):
        for fn in os.listdir(path):
            fp = os.path.join(path, fn)
            if os.path.isdir(fp):
                _scan(fp)
            else:
                fbase = os.path.basename(fp)
                fname, fext = os.path.splitext(fbase)
                if fext == '.py' and fname[0] != '_':
                    # Record full paths first, so the nodes/crawlers
                    # will be able to import each others through
                    # `from stocklab.runtime import *`
                    curr_bundle['files'].append(fp)
    _scan(bundle_base)

    # This is where the import from `stocklab.runtime` will be executed
    for fp in curr_bundle['files']:
        register(subject=fp, bundle=-1)

def register(subject, bundle=0):
    """ Register a node/crawler so that it can be found under
    `stocklab.nodes` or `stocklab.crawlers` for all nodes.
    
    :param subject: Could be the path to the file defines
        the node/crawler, or a class object inherets `Node`/`Crawler`.
    :param bundle: The index of the bundle, defaults to the default bundle.
    :returns: None
    :raises NotImplementedError: TODO
    """
    global __bundle
    # TODO: check if already registered
    if os.path.isfile(subject):
        from .node import Node
        name = os.path.basename(os.path.splitext(subject)[0])
        spec = importlib.util.spec_from_file_location(name, location=subject)
        assert spec, f"stocklab module {name} not found."
        target_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(target_module)
        cls = getattr(target_module, name)
        assert issubclass(cls, Node) or issubclass(cls, Crawler)
        if issubclass(cls, Node):
            __bundles[bundle]['nodes'][name] = cls
        else:
            __bundles[bundle]['crawlers'][name] = cls
    else:
        raise NotImplementedError()

def __get(name, what):
    print('bundle.__get', name, what)
    for bndl in __bundles:
        if name in bndl[what]:
            return bndl[what][name]()
    return None

def get_node(name):
    return __get(name, what='nodes')

def get_crawler(name):
    return __get(name, what='crawlers')
