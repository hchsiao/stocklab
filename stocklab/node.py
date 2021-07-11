from .core.node import Node
from .config import get_config

class DataNode(Node):
    def _resolve(self, **kwargs):
        # TODO: explain this if-condition
        if not hasattr(self, 'schema') and not hasattr(self, 'db_dependencies'):
            kwargs['self'] = self # Call-style adaption
            return self.evaluate(**kwargs)
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
                kwargs['self'] = self # Call-style adaption
                retval = self.evaluate(**kwargs)

            while retval is None:
                try:
                    kwargs['self'] = self # Call-style adaption
                    retval = self.evaluate(**kwargs)
                except CrawlerTrigger as t:
                    self.logger.info(f'Data({args._path}) does not exist in DB, crawling...')
                    if get_config('force_offline') == True:
                        raise NoLongerAvailable('Please unset' +\
                                'force_offline option to enable crawlers')
                    db.update(self, self.crawler_entry(**t.kwargs))
        # TODO: refactor ENDS
        self.db = None
        return retval
