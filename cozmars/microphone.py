import asyncio
import numpy as np
from . import error, util

class MicrophoneOutputStream(util.SyncAsyncRPCStream):
    def _decode(self, data):
        return np.frombuffer(data, dtype='int16')

class Microphone(util.StreamComponent):
    def __init__(self, robot, samplerate, q_size):
        util.StreamComponent.__init__(self, robot)
        self._q_size = q_size
        self._samplerate = samplerate

    def _get_rpc(self):
        rpc = self.rpc.microphone(self.samplerate, q_size=self._q_size)
        self._output_stream = MicrophoneOutputStream(rpc.response_stream, None if self._mode=='aio' else self._loop)
        return rpc

    @property
    def samplerate(self):
        return self._samplerate

    @samplerate.setter
    def samplerate(self, sr):
        if not self.closed:
            raise error.CozmarsError('Cannot set samplerate while microphone is recording')
        self._samplerate = sr

    @property
    def output_stream(self):
        if self.closed:
            raise error.CozmarsError('Microphone is closed')
        return self._output_stream

