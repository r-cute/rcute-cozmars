from . import error, util

class Microphone(util.Component):
    def __init__(self, robot, samplerate, q_size):
        util.Component.__init__(self, robot)
        self._samplerate = samplerate
        self._q_size = q_size
        self._closed = True
        self._stream_task = None

    @property
    def closed(self):
        return not self._stream_task or self._stream_task.done()

    @property
    def samplerate(self):
        return self._samplerate

    @samplerate.setter
    def samplerate(self, samplerate):
        if not self.closed:
            raise error.CozmarsError('Cannot change samplerate when microphone is running')
        self._samplerate = samplerate

    @util.mode()
    async def open(self, samplerate=None):
        if samplerate:
            self.samplerate = samplerate
        if self.closed:
            self._stream_task = self.rpc.mic(self.samplerate)
            await self._stream_task.request()

    @util.mode()
    async def close(self):
        if not self.closed:
            self._stream_task.cancel()

    async def data(self, samplerate=None):
        await self.open(samplerate)
        return self._stream_task.response_stream

    # playback
