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

from .error import ExceptionWithInfo

__bundles = []

def _reset():
    """
    This is only used for testing.  To get a fresh session, we should
    reset `config`, `bundle` and `logger` modules by calling their `reset()`.
    """
    global __bundles
    __bundles = []
    default_bundle = {
            'base': None, 'files': [], 'nodes': {}, 'crawlers': {}
            }
    __bundles.append(default_bundle)

def bundle(bundle_path):
    """
    Scan the bundle from a directory recursively and register Nodes and
    Crawlers.  Only files with a name ends with `.py`, starts with a capital
    letter, and not in a hidden folder will be registered by this function.
    
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
    __bundles.append({
        'base': bundle_base, 'files': [], 'nodes': {}, 'crawlers': {}})
    curr_bundle = __bundles[-1]

    # Scan the bundle folder for nodes and crawlers recurrsively
    def _scan(path):
        for fn in os.listdir(path):
            if fn.startswith('.'):
                continue
            fp = os.path.join(path, fn)
            if os.path.isdir(fp):
                _scan(fp)
            else:
                fbase = os.path.basename(fp)
                fname, fext = os.path.splitext(fbase)
                if fext == '.py' and not fname.startswith('_') \
                        and fname[0].isupper():
                    # Record full paths first, so the nodes/crawlers
                    # will be able to import each others through
                    # `from stocklab.core.runtime import *`
                    curr_bundle['files'].append(fp)
    _scan(bundle_base)

    # This is where the import from `stocklab.core.runtime` will be executed
    for fp in curr_bundle['files']:
        register(subject=fp, bundle=-1)

def register(subject, bundle=0, allow_overwrite=False):
    """
    Register a node/crawler so that it can be found under
    `stocklab.nodes` or `stocklab.crawlers` for all nodes.
    
    :param subject: The path to the file defines the node/crawler, or the
        class itself.
    :type subject: str, Node, Crawler
    :param bundle: The index of the bundle in `__bundles`, defaults to 0 (the
        default bundle).
    :type bundle: int
    :param allow_overwrite: Controls if `subject` can replace another
        component which was already registered.
    :type allow_overwrite: bool
    :returns: None
    :raises AssertionError: An assertion will fail if the component name was
        already registered and `allow_overwrite` is not set.
    """
    global __bundle

    if type(subject) is str and os.path.isfile(subject):
        name = os.path.basename(os.path.splitext(subject)[0])
        spec = importlib.util.spec_from_file_location(name, location=subject)
        assert spec, f"stocklab module {name} not found."
        target_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(target_module)
        assert hasattr(target_module, name), \
                f'File {subject} does not have an object named {name}.'
        cls = getattr(target_module, name)
    else:
        cls = subject
        name = cls.__name__

    from .node import Node
    from .crawler import Crawler
    if issubclass(cls, Node):
        subtype = 'nodes'
    elif issubclass(cls, Crawler):
        subtype = 'crawlers'
    else:
        raise NotImplementedError()

    assert allow_overwrite or name not in __bundles[bundle][subtype]
    __bundles[bundle][subtype][name] = cls

def _get(name, what, xcpt=True):
    for bndl in __bundles:
        if name in bndl[what]:
            return bndl[what][name]()
    if xcpt:
        raise ExceptionWithInfo(
                f'Cannot find {name} in bundles for type {what}.', __bundles)
    return None

def get_node(name):
    return _get(name, what='nodes')

def get_crawler(name):
    return _get(name, what='crawlers')

_reset()
