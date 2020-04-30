import abc
import logging
from datetime import datetime
import re

import stocklab
from stocklab.error import NoLongerAvailable
from stocklab.crawler import CrawlerTrigger
from stocklab.datetime import datetime_to_timestamp, now, in_time_window
from stocklab.db import get_db

class Module(metaclass=abc.ABCMeta):
  def __init__(self):
    self.cache = {}
    self.logger = stocklab.create_logger(self.name)

    # setup crawler
    if 'crawler_entry' in self.spec:
      name_list = self.spec['crawler_entry'].split('.')
      self.crawler = stocklab.get_crawler(name_list[0])
      if len(name_list) == 1:
        self.crawler_entry = self.crawler
      else:
        obj = self.crawler
        for n in name_list[1:]:
          obj = getattr(obj, n)
        self.crawler_entry = obj
    super().__init__()

  @property
  def name(self):
    return type(self).__name__

  @property
  def spec(self):
    return type(self).spec

  @abc.abstractmethod
  def evaluate(self, db, args):
    pass

  def peek(self, db, args):
    raise NotImplementedError()

  def update(self):
    raise NotImplementedError()

  def type_validator(self, retval):
    return retval is not None

  def args_validator(self, arg_spec):
    return True

  def _eval(self, path, peek=False):
    use_cache = 'disable_cache' not in self.spec or not self.spec['disable_cache']
    if path in self.cache and use_cache and not peek:
      return self.cache[path]
    assert not re.search(r'\(((?!\)).)*?\(', path), f'expression cannot have nested parentheses: {path}'
    
    splited = [e.strip('()') for e in re.split(r'(\(.*?\)|\.)', path) if e and e != '.']
    mod_name = splited[0]
    assert self.name == mod_name, f'{splited}'
    arg_spec = self.spec['args']
    assert self.args_validator(arg_spec)
    assert len(arg_spec) == len(splited) - 1, f'invalid expression: {path}'

    from collections.abc import Iterable
    _replace = lambda t, i, elem: t[:i] + [elem] + t[i+1:]
    for i in range(len(splited)):
      field = splited[i]
      try:
        float(field)
        continue
      except ValueError:
        pass
      if '$' != field[0]:
        continue
      values = stocklab.metaevaluate(field.lstrip('$'))
      assert isinstance(values, Iterable)
      return [
          stocklab.evaluate('.'.join(
            [f'({s})' for s in _replace(splited, i, str(val))]
            ))
          for val in values]

    args_list = tuple(splited[1:])
    args = stocklab.Args(args_list, arg_spec)

    result = self._eval_in_context(args, peek=peek)
    if not peek:
      assert self.type_validator(result)
      if use_cache:
        self.cache[path] = result
    return result

  def _eval_in_context(self, args, peek=False):
    if 'schema' not in self.spec and 'db_dependencies' not in self.spec:
      assert not peek
      return self.evaluate(None, args)

    with stocklab.get_db('database') as db:
      if 'schema' in self.spec:
        db.declare_table(self.name, self.spec['schema'])
      if 'db_dependencies' in self.spec:
        for dep in self.spec['db_dependencies']:
          _mod = stocklab.get_module(dep)
          assert 'schema' in _mod.spec, 'cannot depend on modules that do not have a schema'
          db.declare_table(dep, _mod.spec['schema'])
      if 'schema' not in self.spec:
        assert not peek
        return self.evaluate(db, args)

      while True:
        _f = self.peek if peek else self.evaluate
        try:
          return _f(db, args)
        except CrawlerTrigger as t:
          self.logger.info(f'Data({args._path}) does not exist in DB, crawling...')
          if stocklab.config['force_offline']:
            raise NoLongerAvailable('Please unset' +\
                'force_offline option to enable crawlers')
          db.update(self, self.crawler_entry(**t.kwargs))

  def set_last_update_datetime(self):
    tstmp = datetime_to_timestamp(now())
    stocklab.set_state(f'{self.name}__t_last_update', str(tstmp))
  
  def last_update_datetime(self):
    t_last_update = stocklab.get_state(f'{self.name}__t_last_update')
    if t_last_update:
      return datetime.utcfromtimestamp(int(t_last_update))
    else:
      return None
  
  def is_outdated(self):
    kwargs = {}
    if 'update_offset' in self.spec:
      kwargs['offset'] = self.spec['update_offset']
    if 'update_period' in self.spec:
      kwargs['period'] = self.spec['update_period']
  
    last_update = self.last_update_datetime()
    if last_update:
      return not in_time_window(last_update, **kwargs)
    else:
      return True

class MetaModule(Module):
  def __init__(self):
    super().__init__()

  def db_is_fresh(self, db, last_crawl):
    if last_crawl is None:
      self.logger.info(f'Start default meta-module refresh routine')
      raise CrawlerTrigger()
    else:
      self.logger.info(f'Refresh ends')

  def update(self):
    if 'schema' not in self.spec:
      # module has nothing to do with DB & to update
      return
    if not self.is_outdated():
      return
    with get_db('database') as db:
      db.declare_table(self.name, self.spec['schema'])
      last_crawl = None
      while True:
        try:
          self.db_is_fresh(db, last_crawl)
        except CrawlerTrigger as t:
          last_crawl = t.kwargs
          if stocklab.config['force_offline']:
            raise NoLongerAvailable('Please unset' +\
                'force_offline option to enable crawlers')
          self.logger.info(f'Refresh required, preparing...')
          db.update(self, self.crawler_entry(**t.kwargs))
          self.set_last_update_datetime()
        else:
          break
