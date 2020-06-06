from . import error, util

class Camera(util.Component):
    def __init__(self, robot, q_size):
        util.Component.__init__(self, robot)
        self._q_size = q_size
        self._stream_rpc = None
        self.default_framerate = 10
        self.default_resolution = (320, 240)

    @property
    def closed(self):
        return not self._stream_rpc or self._stream_rpc.done()

    @util.mode()
    async def open(self, resolution=None, framerate=None):
        if self.closed:
            w, h = resolution or self.default_resolution
            self._stream_rpc = self.rpc.camera(w, h, framerate or self.default_framerate, q_size=self._q_size)
            self._stream_rpc.request()

    @util.mode()
    async def close(self):
        if not self.closed:
            self._stream_rpc.cancel()

    @util.mode()
    async def capture(self, options):
        if self.closed:
            return await self.rpc.capture(options)
        else:
            raise error.CozmarsError('Cannot take a photo while camera is streaming video')

    @util.mode()
    async def frames(self, resolution=None, framerate=None):
        if self.closed:
            raise CozmarsError('Camera is closed')
        # await self.open(resolution, framerate)
        return self._stream_rpc.response_stream

    async def __aenter__(self):
        await self.open()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    def __enter__(self):
        self.open()

    def __exit__(self, exc_type, exc, tb):
        self.close()

