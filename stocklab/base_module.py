import abc
import logging
from datetime import datetime

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

  def _eval(self, path, peek=False):
    use_cache = 'disable_cache' not in self.spec or not self.spec['disable_cache']
    if path in self.cache and use_cache and not peek:
      return self.cache[path]
    else:
      mod_name = path.split('.')[0]
      assert self.name == mod_name
      args_list = tuple(path.split('.')[1:])
      try:
        arg_spec = self.spec['args']
      except:
        self.logger.error("Cannot find attribute: spec")
        return None
      assert len(arg_spec) == len(args_list)
      args = stocklab.Args(args_list, arg_spec)

      result = self._eval_in_context(args, peek=peek)
      if use_cache and not peek:
        self.cache[path] = result
      return result

  def _eval_in_context(self, args, peek=False):
    if 'schema' not in self.spec:
      assert not peek
      return self.evaluate(None, args)
    with stocklab.get_db('database') as db:
      db.declare_table(self.name, self.spec['schema'])
      if 'db_dependencies' in self.spec:
        for dep in self.spec['db_dependencies']:
          _mod = stocklab.get_module(dep)
          assert 'schema' in _mod.spec, 'cannot depend on modules that do not have a schema'
          db.declare_table(dep, _mod.spec['schema'])
      while True: # TODO: prevent crawl-forever?
        _f = self.peek if peek else self.evaluate
        try:
          return _f(db, args)
        except CrawlerTrigger as t:
          self.logger.info('db miss')
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
      self.logger.info(f'Start default meta-module update routine {self.name}')
      raise CrawlerTrigger()
    else:
      self.logger.info(f'Update routine ends')

  def update(self):
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
          self.logger.info('meta miss')
          db.update(self, self.crawler_entry(**t.kwargs))
          self.set_last_update_datetime()
        else:
          break
