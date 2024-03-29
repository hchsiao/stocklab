"""TODO: refactor this entire file."""
import pydal
from contextlib import ContextDecorator

from .core.logger import get_instance as get_logger
from .core.config import get_config

def _get_keys(schema):
  return [field_name
      for field_name, field_config in schema.items()
      if 'key' in field_config and field_config['key']
      ]

class get_db(pydal.DAL, ContextDecorator):
  _cfg_inst = {}
  _inst_cnt = {}
  def __init__(self, config_name, *args, **kwargs):
    self.__args = args
    self.__kwargs = kwargs
    self.config_name = config_name
    if config_name not in get_db._inst_cnt:
      get_db._inst_cnt[config_name] = 1
    else:
      get_db._inst_cnt[config_name] += 1

  def __enter__(self):
    if get_db._inst_cnt[self.config_name] > 1:
      self._singleton = get_db._cfg_inst[self.config_name]
      return self._singleton
    else:
      self._singleton = None
    self.config = get_config(self.config_name)
    assert self.config, f'Failed to get config: {self.config_name}'
    self.logger = get_logger(f'stocklab_db__{self.config_name}')
    get_db._cfg_inst[self.config_name] = self

    assert self.config['type'] in ['sqlite', 'mssql']
    if self.config['type'] == 'sqlite':
      import os
      db_path = os.path.join(get_config('root_dir'), self.config['filename'])
      uri = f'sqlite://{db_path}'
    elif self.config['type'] == 'mssql':
      host = self.config['host']
      user = self.config['user']
      password = self.config['password']
      driver = self.config['driver']
      uri = f'mssql4://{user}:{password}@{host}/stocklab-db?driver={driver}'

    self.__kwargs['folder'] = get_config('root_dir')
    if 'rebuild_metadata' in self.config and self.config['rebuild_metadata']:
      self.__kwargs['fake_migrate_all'] = True # see pyDAL's 'migration'
    super().__init__(uri=uri, *self.__args, **self.__kwargs)
    return self

  def __exit__(self, err_type, err_value, traceback):
    get_db._inst_cnt[self.config_name] -= 1
    db = self._singleton or self
    if isinstance(err_type, Exception):
      db.logger.error(err_value)
    if get_db._inst_cnt[self.config_name] == 0:
      db.commit()
      db.close()
    return False # do not eliminate error
  
  def declare_table(self, name, schema):
    def _field(name, config):
      assert name != 'id', 'pyDAL reserved this name'
      _cfg = config.copy()
      try: # pop-out params not used by pyDAL
        _cfg.pop('key')
        _cfg.pop('pre_proc')
      except KeyError:
        pass
      return pydal.Field(name, **_cfg)
    if name not in self.tables:
      fields = [_field(field_name, schema[field_name])
          for field_name in schema.keys()]
      self.define_table(name, *fields)

  def update(self, node, res):
    assert type(res) is list
    assert all([type(rec) is dict for rec in res])
    schema = node.schema
    ignore_existed = node.ignore_existed
    update_existed = node.update_existed
    assert not (ignore_existed and update_existed)

    def _proc(key, val):
      cfg = schema[key]
      field_type = cfg['type'] if 'type' in cfg else 'string'
      type_map = {
          'string': str,
          'text': str,
          'integer': int,
          }
      processed = cfg['pre_proc'](val) if 'pre_proc' in cfg else val
      if field_type in type_map.keys() and processed is not None:
        assert type(processed) is type_map[field_type], 'type error in DB insertion.' +\
            f' Field {key} requires {field_type}, got {type(processed)}'
      return processed

    def _key_q(schema):
      key_fields = _get_keys(schema)
      queries = [table[k] == v for k, v in rec.items() if k in key_fields]
      assert len(key_fields) > 0
      def _and(qs):
        if len(qs) == 1:
          return qs[0]
        else:
          return qs[0] & _and(qs[1:])
      return _and(queries)

    table = self[node.name]
    for rec in res:
      rec = {k:_proc(k, v) for k, v in rec.items()}
      if ignore_existed:
        if not self[node.name](_key_q(schema)):
          self[node.name].insert(**rec)
      elif update_existed:
        self[node.name].update_or_insert(_key_q(schema), **rec)
      else:
        self[node.name].insert(**rec)
