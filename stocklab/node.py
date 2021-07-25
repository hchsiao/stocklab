from .core.node import Node, Arg, Args
from .core.config import get_config
from .core.crawler import CrawlerTrigger

class DataNode(Node):
    """
    Nodes with a database backend.

    Attrubutes:

    *  ignore_existed: The key of a new record may be existed in the
        database. Keep the old record if the key duplicates. (defaults to:
        False)
    *  update_existed: The key of a new record may be existed in the
        database. Keep the new record if the key duplicates. (defaults to:
        False)
    """
    def __init__(self):
        super().__init__()
        self.db = None
        self.default_attr('ignore_existed', False)
        self.default_attr('update_existed', False)

    def _resolve(self, **kwargs):
        # TODO: explain this if-condition
        if not hasattr(self, 'schema') and not hasattr(self, 'db_dependencies'):
            return super()._resolve(**kwargs)
        else:
            return self._resolve_with_db(**kwargs)

    def _resolve_with_db(self, **kwargs):
        retval = None
        from .db import get_db
        # TODO: refactor STARTS
        with get_db('database') as db:
            self.db = db
            if hasattr(self, 'schema'):
                db.declare_table(self.name, self.schema)
            if hasattr(self, 'db_dependencies'):
                for dep in self.db_dependencies:
                    raise NotImplementedError()
            if not hasattr(self, 'schema'):
                retval = type(self).evaluate(**kwargs)

            while retval is None:
                try:
                    retval = type(self).evaluate(**kwargs)
                except CrawlerTrigger as t:
                    path = self.path(**kwargs)
                    self.logger.info(f'{path} does not exist in DB, crawling...')
                    if get_config('force_offline') == True:
                        raise NoLongerAvailable('Please unset' +\
                                'force_offline option to enable crawlers')
                    db.update(self, type(self).crawler_entry(**t.kwargs))
        # TODO: refactor ENDS
        self.db = None
        return retval

class Schema(dict):
    pass
