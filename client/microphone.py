from . import error, util

class Microphone(util.Component):
    def __init__(self, robot, q_size):
        util.Component.__init__(self, robot)
        self._q_size = q_size
        self.default_samplerate = 16000
        self._closed = True
        self._stream_task = None

    @property
    def closed(self):
        return not self._stream_task or self._stream_task.done()

    @util.mode()
    async def open(self, samplerate=None):
        if self.closed:
            self._stream_task = self.rpc.mic(samplerate or self.default_samplerate)
            await self._stream_task.request()

    @util.mode()
    async def close(self):
        if not self.closed:
            self._stream_task.cancel()

    async def data(self, samplerate=None):
        await self.open(samplerate)
        return self._stream_task.response_stream

    # playback
