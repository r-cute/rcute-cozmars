import functools
import asyncio
from concurrent import futures
from wsmprpc import RPCStream
from PIL import ImageColor
from os import path

PKG = path.dirname(__file__)
RESOURCE = path.join(PKG, 'resources')

def resource(file_name):
    return path.join(RESOURCE, file_name)

def pkg(file_name):
    return path.join(PKG, file_name)

def bgr(color):
    if isinstance(color, str):
        return ImageColor.getrgb(color)[::-1]
    else:
        return color

def sample_width(dtype):
    return {'int16':2, 'float32':4, 'float64':8, 'int8':1, 'int32':4}[dtype]

def mode(force_sync=True, property_type=None):
    def func_deco(func):

        @functools.wraps(func)
        def new_func(*args, **kwargs):
            if not asyncio.iscoroutinefunction(func):
                raise ImportError('Cannot decorate connection.mode on non-coroutine function')

            self = args[0]
            if self._in_event_loop():
                return functools.partial(func, self) if property_type else func(*args, **kwargs)

            fut = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self._lo)

            if force_sync or property_type or self._mode == 'sync':
                try:
                    return fut.result(kwargs.pop('timeout', None))
                except futures.TimeoutError:
                    return None
            else: # mode == 'async'
                return fut

        if property_type == 'getter':
            return property(new_func)
        elif property_type == 'setter':
            return property(new_func).setter(new_func)
        else:
            return new_func

    return func_deco

class withmixin:
    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    def __enter__(self):
        if self._mode == 'aio':
            raise AttributeError('__enter__')
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

class Component:
    def __init__(self, robot):
        self._robot = robot

    @property
    def _mode(self):
        return self._robot._mode

    @property
    def _lo(self):
        return self._robot._lo

    @property
    def _rpc(self):
        return self._robot._rpc

    def _in_event_loop(self):
        return self._robot._in_event_loop()

class StreamComponent(Component):
    def __init__(self, robot):
        Component.__init__(self, robot)
        self._stream_rpc = None

    @property
    def closed(self):
        """Is the data stream closed"""
        return not self._stream_rpc or self._stream_rpc.done()


    def _get_rpc(self):
        '''
        this method is responsible for calling rpc and creating coresponding stream
        '''
        raise NotImplementedError

class InputStreamComponent(StreamComponent, withmixin):
    def __init__(self, robot):
        StreamComponent.__init__(self, robot)

    @mode()
    async def close(self):
        if not self.closed:
            try:
                self._input_stream.force_put_nowait(StopAsyncIteration())
                await self._stream_rpc
            except asyncio.CancelledError:
                pass

    @mode()
    async def open(self):
        if self.closed:
            self._input_stream = RPCStream()
            self._stream_rpc = self._get_rpc()
            self._stream_rpc.request()


class OutputStream(RPCStream, withmixin):
    """Output Data Stream"""
    def __init__(self, parent, maxsize=0):
        RPCStream.__init__(self, maxsize)
        self._parent = parent

    @property
    def _lo(self):
        return self._parent._component._lo

    @property
    def _mode(self):
        return self._parent._component._mode

    def _in_event_loop(self):
        return self._parent._component._in_event_loop()

    @mode()
    async def open(self):
        """Open data stream"""
        await self._parent.add_stream(self)

    @mode()
    async def close(self):
        """Close data flow"""
        await self._parent.remove_stream(self)

    @mode()
    async def read(self):
        """Read a frame of data from the data stream"""
        return await self.__anext__()

    def __iter__(self):
        if self._mode == 'aio':
            raise AttributeError('__iter__')
        return self

    def __next__(self):
        return self.read()


class MultiplexOutputStream:
    def __init__(self, component):
        self._output_streams = set()
        self._component = component

    async def add_stream(self, stream):
        self._output_streams.add(stream)
        if len(self._output_streams) == 1:
            await self._component.open()

    async def remove_stream(self, stream):
        try:
            self._output_streams.remove(stream)
            if len(self._output_streams) == 0:
                await self._component.close()
        except KeyError:
            pass

    def force_put_nowait(self, o):
        # see `wsmprpc.RPCStream
        for s in self._output_streams:
            s.force_put_nowait(o)


class MultiplexOutputStreamComponent(StreamComponent):
    def __init__(self, robot, q_size, multiplex_output_stream):
        StreamComponent.__init__(self, robot)
        self._q_size = q_size
        self._multiplex_output_stream = multiplex_output_stream

    async def _async_get_buffer(self):
        return OutputStream(self._multiplex_output_stream, maxsize=self._q_size)

    def get_buffer(self):
        """Get output data stream
        """
        if self._in_event_loop():
            return OutputStream(self._multiplex_output_stream, maxsize=self._q_size)
        else:
            return asyncio.run_coroutine_threadsafe(self._async_get_buffer(), self._lo).result()

    @mode()
    async def close(self):
        if not self.closed:
            self._stream_rpc.cancel()

    @mode()
    async def open(self):
        if self.closed:
            self._stream_rpc = self._get_rpc()
            self._stream_rpc.request()
