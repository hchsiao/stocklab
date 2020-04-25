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
          self.logger.info(f'Today ({today}) is not trade date')
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

