"""
This module provides serveral utilities which is not mandatory for stocklab
to excecute, but these are common patterns for crawlers in applications.
"""

import time

from .core.crawler import *
from .core.logger import get_instance as get_logger

class SpeedLimiter:
    """
    A helper class to limit the frequency of a function call (e.g. remote
    access).
    """
    def __init__(self, func, max_speed, tick_period):
        super().__init__()
        self.func = func
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
        retval = self.func(*args, **kwargs)
        get_logger().debug(f'Request sent, speed={speed} (from SpeedLimiter)')
        self.last_req = time.time()
        return retval

def speed_limiter(max_speed, tick_period=0.01):
    """
    The decorator for `SpeedLimiter`.  Use it like::

        @speed_limiter(max_speed=10)
        def my_action(myparam):
            do_something()

    :param max_speed: The peak throughput limitation. Specified the number in
        `call/second`.
    :type max_speed: float
    :param tick_period: The cooldown interval in seconds, defaults to 0.01.
    :type tick_period: float
    """
    return lambda f: SpeedLimiter(f, max_speed, tick_period)

class RetryHelper:
    """
    A helper class to re-do a function on certain exceptions.
    """
    def __init__(self, func, max_retry, interval, retry_on):
        assert max_retry >= 0
        super().__init__()
        self.func = func
        self.max_retry = max_retry
        self.interval = interval
        self.retry_on = retry_on

    def __call__(self, *args, **kwargs):
        retry_count = 0
        while True:
            try:
                return self.func(*args, **kwargs)
            except Exception as e:
                if isinstance(e, self.retry_on):
                    retry_count += 1
                    if retry_count > self.max_retry:
                        raise e
                    e_name = type(e).__name__
                    e_msg = str(e)
                    e_str = f'{e_name}({e_msg})' if e_msg else e_name
                    get_logger().info(f'Got {e_str}, waiting for '
                            'retry... (from RetryHelper)')
                    time.sleep(self.interval)
                else:
                    raise e

def retry_helper(max_retry, interval=5, retry_on=(Exception,)):
    """
    The decorator for `SpeedLimiter`.  Use it like::

        @speed_limiter(max_speed=10)
        def my_action(myparam):
            do_something()

    :param max_retry: The retry count limitation.
    :type max_retry: int
    :param interval: The retry interval in seconds, defaults to 5.
    :type interval: float
    :param retry_on: The tuple of `Exception`s to retry, defaults to
        `[Exception]`.
    :type retry_on: list
    """
    return lambda f: RetryHelper(f, max_retry, interval, retry_on)
