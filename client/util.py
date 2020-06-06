import functools
import asyncio
from concurrent import futures
from .wsmprpc import RPCStream

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


class StreamComponent(Component):
    def __init__(self, robot):
        Component.__init__(self, robot)
        self._stream_rpc = None

    @property
    def closed(self):
        return not self._stream_rpc or self._stream_rpc.done()

    @mode()
    async def close(self):
        if not self.closed:
            self._stream_rpc.cancel()
            try:
                await self._stream_rpc
            except asyncio.CancelledError:
                pass
    def open(self):
        raise NotImplementedError

    async def __aenter__(self):
        await self.open()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    def __enter__(self):
        self.open()

    def __exit__(self, exc_type, exc, tb):
        self.close()


class InputStreamComponent(StreamComponent):

    @mode()
    async def open(self):
        if self.closed:
            self._input_stream = RPCStream()
            self._stream_rpc = getattr(self.rpc, '')
            self._stream_rpc.request()

    @property
    @sync_stream
    def input_stream(self):
        if self.closed:
            raise error.CozmarsError(f'{self.__class__.__name__} is closed')
        return self._input_stream


class OutputStreamComponent(StreamComponent):

    @mode()
    async def open(self):
        if self.closed:
            self._stream_rpc = None
            self._stream_rpc.request()

    @property
    @sync_stream
    def output_stream(self):
        if self.closed:
            raise error.CozmarsError(f'{self.__class__.__name__} is closed')
        return self._stream_rpc.respoonse_stream



class async_to_sync_stream:
    def __init__(async_stream):
        self.astream = async_stream
    def __iter__(self):
        return self
    def __next__(self):
        return asyncio.run_coroutine_threadsafe(self.astream.__anext__()).result()

def sync_stream(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        self = args[0]
        ret = func(*args, **kwargs)
        return ret if self._mode is 'aio' else async_to_sync_stream(ret)
    return new_func

def mode(force_sync=True, property_type=None):
    def func_deco(func):

        @functools.wraps(func)
        def new_func(*args, **kwargs):
            if not asyncio.iscoroutinefunction(func):
                raise error.CozmarsError('Cannot decorate connection.mode on non-coroutine function')

            self = args[0]
            if self._mode == 'aio':
                return functools.partial(func, self) if property_type else func(*args, **kwargs)

            fut = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self._loop)

            if self._mode == 'sync' or force_sync or property_type:
                try:
                    return fut.result(kwargs.pop('timeout', None))
                except futures.TimeoutError:
                    return None
            else: # _mode == 'async'
                return fut

        if property_type == 'getter':
            return property(new_func)
        elif property_type == 'setter':
            return property(new_func).setter(new_func)
        else:
            return new_func

    return func_deco

