import time

from .core.crawler import *

# Decorators

class SpeedLimiter:
    """
    Parameters: max_speed, tick_period (optional)
    """
    def __init__(self, request_func, max_speed, tick_period):
        super().__init__()
        self.request_func = request_func
        self.max_speed = max_speed
        self.tick_period = tick_period
        self.last_req = None

    def speed(self):
        if self.last_req is None:
            return 0.0
        now = time.time()
        return 1.0 / (now - self.last_req)

    def __call__(self, *args, **kwargs):
        speed = self.speed()
        while self.speed() > self.max_speed:
            time.sleep(self.tick_period)
            speed = self.speed()
        retval = self.request_func(*args, **kwargs)
        self.logger.debug(f'Request sent, speed={speed}')
        self.last_req = time.time()
        return retval

def speed_limiter(max_speed, tick_period=0.01):
    return lambda f: SpeedLimiter(f, max_speed, tick_period)

class RetryMixin(object):
    """
    Parameters: retry_limit, retry_period
    """
    def __init__(self):
        assert isinstance(self, Crawler)
        super().__init__()

        # Parameters
        assert hasattr(self, 'retry_limit')
        assert hasattr(self, 'retry_period')

    def retry_when_failed(self, do_cb, success_cb, error_cb):
        for nth_try in range(self.retry_limit + 1):
            try:
                res = do_cb()
            except Exception as e:
                if nth_try < self.retry_limit:
                    self.logger.info(f'got error: {e}, waiting for retry')
                    time.sleep(self.retry_period)
                    continue
                else:
                    raise e
            if success_cb(res):
                return res
            self.logger.info('got wrong data, waiting for retry')
            time.sleep(self.retry_period)
        raise error_cb(res)
