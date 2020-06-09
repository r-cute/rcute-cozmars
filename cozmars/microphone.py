import asyncio
import numpy as np
from . import error, util

class MicrophoneOutputStream(util.SyncAsyncRPCStream):
    def __init__(self, async_stream, loop, dtype):
        util.SyncAsyncRPCStream.__init__(self, async_stream, loop)
        self._dtype = dtype
    def _decode(self, data):
        return np.frombuffer(data, dtype=self._dtype)

class Microphone(util.StreamComponent):
    def __init__(self, robot, samplerate, dtype, q_size):
        util.StreamComponent.__init__(self, robot)
        self._q_size = q_size
        self._samplerate = samplerate
        self._dtype = dtype

    def _get_rpc(self):
        rpc = self.rpc.microphone(self.samplerate, self.dtype, q_size=self._q_size)
        self._output_stream = MicrophoneOutputStream(rpc.response_stream, None if self._mode=='aio' else self._loop, self.dtype)
        return rpc

    @property
    def dtype(self):
        return self._dtype

    @dtype.setter
    def dtype(self, dt):
        if not self.closed:
            raise error.CozmarsError('Cannot set dtype while microphone is recording')
        self._dtype = dt

    @property
    def channels(self):
        return 1

    @property
    def samplerate(self):
        return self._samplerate

    @samplerate.setter
    def samplerate(self, sr):
        if not self.closed:
            raise error.CozmarsError('Cannot set samplerate while microphone is recording')
        self._samplerate = sr

    @util.mode(property_type='setter')
    async def volumn(self, *args):
        return await self.rpc.microphone_volumn(*args)

    @property
    def output_stream(self):
        if self.closed:
            raise error.CozmarsError('Microphone is closed')
        return self._output_stream

