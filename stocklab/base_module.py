import abc
import logging

import stocklab
from stocklab.error import NoLongerAvailable
class Module(metaclass=abc.ABCMeta):
  def __init__(self):
    self.cache = {}
    self.logger = stocklab.create_logger(self.name)

    # setup crawler
    if 'crawler' in self.spec:
      name_list = self.spec['crawler'].split('.')
      self.crawler = stocklab.get_crawler(name_list[0])
      if len(name_list) == 1:
        self.parser = self.crawler
      else:
        obj = self.crawler
        for n in name_list[1:]:
          obj = getattr(obj, n)
        self.parser = obj
    super().__init__()

  @property
  def name(self):
    return type(self).__name__

  @property
  def spec(self):
    return type(self).spec

  def evaluate(self, path, peek=False):
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

      if peek:
        result = self.access_db(args, peek=True)
      else:
        result = self.run(args)
      if use_cache and not peek:
        self.cache[path] = result
      return result

  @abc.abstractmethod
  def run(self, args):
    raise NotImplementedError()

  def peak_db(self, db, args):
    raise NotImplementedError()

  def peek(self, args):
    return self.evaluate(args, peek=True)

  def access_db(self, args, peek=False):
    query_res = None
    with stocklab.get_db('database') as db:
      if 'schema' in self.spec:
        db.declare_table(self.name, self.spec['schema'])
      if 'db_dependencies' in self.spec:
        for dep in self.spec['db_dependencies']:
          _mod = stocklab.get_module(dep)
          assert 'schema' in _mod.spec, 'cannot depend on modules that do not have a schema'
          db.declare_table(dep, _mod.spec['schema'])
      while True:
        if peek:
          query_res, db_miss, crawl_args = self.peak_db(db, args)
        else:
          query_res, db_miss, crawl_args = self.query_db(db, args)
        if db_miss:
          self.logger.info('db miss')
          if stocklab.config['force_offline']:
            raise NoLongerAvailable('Please unset' +\
                'force_offline option to enable crawlers')
          res = self.parser(**crawl_args)
          db.update(self, res)
        else:
          break
    return query_res

class MetaModule(Module):
  def __init__(self):
    super().__init__()

  def check_update(self, db):
    return False, {}
