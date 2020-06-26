import functools
import asyncio
from concurrent import futures
from wsmprpc import RPCStream

class SyncAsyncRPCStream:
    def _decode(self, data):
        return data
    def _encode(self, data):
        return data
    def __init__(self, async_stream, loop):
        self._astream = async_stream
        self._loop = loop
    def __iter__(self):
        return self
    def __next__(self):
        return self._decode(asyncio.run_coroutine_threadsafe(self._astream.__anext__(), self._loop).result())
    def __aiter__(self):
        return self
    async def __anext__(self):
        return self._decode(await self._astream.__anext__())
    def put(self, obj):
        return asyncio.run_coroutine_threadsafe(self._astream.put(self._encode(obj)), self._loop).result()
    def put_nowait(self, obj):
        return self.loop.call_soon_threadsafe(self._astream.put_nowait, self._encode(obj))


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
        await self._close()

    async def _close(self):
        if not self.closed:
            self._stream_rpc.cancel()
            try:
                await self._stream_rpc
            except asyncio.CancelledError:
                pass

    @mode()
    async def open(self):
        await self._open()

    async def _open(self):
        if self.closed:
            self._stream_rpc = self._get_rpc()
            self._stream_rpc.request()

    def _get_rpc(self):
        raise NotImplementedError

    async def __aenter__(self):
        await self._open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()





