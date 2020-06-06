from . import error, util

class Microphone(util.Component):
    def __init__(self, robot, q_size):
        util.Component.__init__(self, robot)
        self._q_size = q_size
        self.default_samplerate = 16000
        self._closed = True
        self._stream_rpc = None

    @property
    def closed(self):
        return not self._stream_rpc or self._stream_rpc.done()

    @util.mode()
    async def open(self, samplerate=None):
        if self.closed:
            self._stream_rpc = self.rpc.microphone(samplerate or self.default_samplerate)
            self._stream_rpc.request()

    @util.mode()
    async def close(self):
        if not self.closed:
            self._stream_rpc.cancel()

    @util.mode()
    async def output_stream(self, samplerate=None):
        if self.closed:
            raise error.CozmarsError('Microphone is closed')
        # await self.open(samplerate)
        return self._stream_rpc.response_stream

    async def __aenter__(self):
        await self.open()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    def __enter__(self):
        self.open()

    def __exit__(self, exc_type, exc, tb):
        self.close()
