from functools import wraps
from datetime import datetime

def timed(func):
    @wraps(func)
    def timed_func(*args, **kwargs):
        start_time = datetime.now()
        ret = func(*args, **kwargs)
        print(f'{func.__name__} - {(datetime.now() - start_time).total_seconds():.4f}')
        return ret
    return timed_func
