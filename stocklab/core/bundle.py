""" This module handles the registration of nodes/crawlers
    and node/crawler collections (bundles).  A `dict` called
    `__bundles` contains the registrated nodes/crawlers.

    *  `__bundles`: A list of registered nodes/crawlers. Each
       bundle is a `dict` with four keys: `base`, `files`, `nodes`
       and `crawlers`.  The default bundle is a `dict` with `base`
       is None.  Other bundles will have `base` set to the path
       to bundle modules.  Other keys represent:

       *  `files`: list of source files.
       *  `nodes`: mapping from node names to the class handle.
       *  `crawlers`: mapping from crawler names to the class handle.
"""
import os
import pathlib
import importlib.util

from .crawler import Crawler
from .error import ExceptionWithInfo

__bundles = [
        {
            'base': None, 'files': [],
            'nodes': {}, 'crawlers': {}}, # The default bundle
        ]

def bundle(bundle_path):
    """
    Scan the bundle from a directory recursively and
    register them.
    
    :param bundle_path: The path to the bundle.
    :type bundle_path: str
    :returns: None
    """
    global __bundles
    # Maintain the entry in __bundle
    if os.path.isfile(bundle_path): # the path points to a file
        bundle_base = str(pathlib.Path(bundle_path).parent.resolve())
    else: # the path points to a directory
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
                    # `from stocklab.core.runtime import *`
                    curr_bundle['files'].append(fp)
    _scan(bundle_base)

    # This is where the import from `stocklab.core.runtime` will be executed
    for fp in curr_bundle['files']:
        register(subject=fp, bundle=-1)

def register(subject, bundle=0):
    """
    Register a node/crawler so that it can be found under
    `stocklab.nodes` or `stocklab.crawlers` for all nodes.
    
    :param subject: The path to the file defines the node/crawler, or the
        class itself.
    :type subject: str, Node, Crawler
    :param bundle: The index of the bundle in `__bundles`, defaults to 0 (the
        default bundle).
    :type bundle: int
    :returns: None
    :raises NotImplementedError: Currently, only registration by file is
        implemented.
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
        assert hasattr(target_module, name), f'File {subject} does not have an object named {name}.'
        cls = getattr(target_module, name)
        assert issubclass(cls, Node) or issubclass(cls, Crawler)
        if issubclass(cls, Node):
            __bundles[bundle]['nodes'][name] = cls
        else:
            __bundles[bundle]['crawlers'][name] = cls
    else:
        raise NotImplementedError()

def _get(name, what, xcpt=True):
    for bndl in __bundles:
        if name in bndl[what]:
            return bndl[what][name]()
    if xcpt:
        raise ExceptionWithInfo(f'Cannot find {name} in bundles for type {what}.', __bundles)
    return None

def get_node(name):
    return _get(name, what='nodes')

def get_crawler(name):
    return _get(name, what='crawlers')
