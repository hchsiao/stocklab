import time

from .core.crawler import *
from .core.logger import get_instance as get_logger

# Decorators

class SpeedLimiter:
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
        get_logger().debug(f'Request sent, speed={speed} (from SpeedLimiter)')
        self.last_req = time.time()
        return retval

def speed_limiter(max_speed, tick_period=0.01):
    return lambda f: SpeedLimiter(f, max_speed, tick_period)
