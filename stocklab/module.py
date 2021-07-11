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

import stocklab
from stocklab.datetime import Date
from stocklab.db import get_db
from stocklab.error import InvalidDateRequested

def _is_iterable_of_type(obj, t):
  from collections.abc import Iterable
  if not isinstance(obj, Iterable):
    return False
  try:
    e = next(iter(obj))
    return type(e) is t
  except StopIteration:
    return True

class StockList(stocklab.MetaModule):
  def __init__(self):
    super().__init__()

  def args_validator(self, arg_spec):
    return len(arg_spec) == 0

  def type_validator(self, retval):
    return _is_iterable_of_type(retval, str)

class Primitive(stocklab.Module):
  def __init__(self):
    super().__init__()

  def args_validator(self, arg_spec):
    return len(arg_spec) == 2 \
        and type(arg_spec[0]) is str \
        and type(arg_spec[1]) is tuple \
        and arg_spec[1][1] is Date

  def peek(self, db, args):
    table = db[self.name]
    query = table.stock_id == args.stock_id
    query &= table.date == args.date.timestamp()
    retval = db(query).select(limitby=(0, 1))
    if not retval:
      raise CrawlerTrigger(stock_id=args.stock_id, date=args.date)

  def db_is_fresh(self, db):
    # TODO: current implementation assumes that stocks_of_interest
    sl = stocklab.get_module(stocklab.config['stocks_of_interest'])
    stock_count = len(stocklab.metaevaluate(f'{sl.name}'))
    table = db[self.name]
    query = table.date == Date.today().timestamp()
    todays_count = len(db(query).select(table.stock_id, distinct=True))

    assert not todays_count > stock_count
    if todays_count == stock_count:
      self.set_last_update_datetime()
      return True
    else:
      return False

  def update(self):
    if not self.is_outdated():
      return
    with get_db('database') as db:
      db.declare_table(self.name, self.spec['schema'])
      sl = stocklab.get_module(stocklab.config['stocks_of_interest'])
      assert isinstance(sl, StockList)
      stock_list = stocklab.metaevaluate(sl.name)
      if not self.db_is_fresh(db):
        if stocklab.config['force_offline']:
          raise NoLongerAvailable('Please unset' +\
              'force_offline option to enable crawlers')
        self.logger.info('Start updating Primitive module')
        today = Date.today()
        try:
          stocklab.peek(f'{self.name}.(${sl.name}).{today}')
        except InvalidDateRequested:
          self.logger.error(f'Today ({today}) is not trade date')
        self.logger.info('End update')

class Sign(stocklab.Module):
  def __init__(self):
    super().__init__()

  def type_validator(self, retval):
    return type(retval) is bool

class CandleStick(stocklab.Module):
  def __init__(self):
    super().__init__()

  def type_validator(self, retval):
    return _is_iterable_of_type(retval, float) and len(retval) == 4

