import functools
import asyncio

class Component:
    def __init__(self, robot):
        self._robot = robot

    @property
    def _mode(self):
        return self._robot._mode

    @property
    def _loop(self):
        return self._robot._loop

    @property
    def rpc(self):
        return self._robot._stub

def mode(force_sync=True):
    def func_deco(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not asyncio.iscoroutinefunction(func):
                raise error.CozmarsError('Cannot decorate connection.mode on non-coroutine function')

            self = args[0]
            if self._mode == 'aio':
                return func(*args, **kwargs)

            fut = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self._loop)

            if self._mode == 'sync' or force_sync:
                try:
                    return fut.result(kwargs.pop('timeout', None))
                except futures.TimeoutError:
                    return None
            else: # _mode == 'async'
                return fut

        return wrapper

    return func_deco

def get_set(func):
    def deco(*args, *kwargs):
        if args[0]._mode = 'aio'
        return func(*args, *kwargs)
        return property(func).setter(func)


def get(func):
    return property(func)
