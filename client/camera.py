from . import error, util

class Camera(util.Component):
    def __init__(self, robot, q_size):
        util.Component.__init__(self, robot)
        self._q_size = q_size
        self._stream_task = None
        self.default_framerate = 10
        self.default_resolution = (320, 240)

    @property
    def closed(self):
        return not self._stream_task or self._stream_task.done()

    @util.mode()
    async def open(self, resolution=None, framerate=None):
        if self.closed:
            w, h = resolution or self.default_resolution
            self._stream_task = self.rpc.cam(w, h, framerate or self.default_framerate, q_size=self._q_size)
            await self._stream_task.request()

    @util.mode()
    async def close(self):
        if not self.closed:
            self._stream_task.cancel()

    @util.mode()
    async def capture(self):
        if self.closed:
            return await self.rpc.capture()
        else:
            # to do
            pass

    async def frames(self, resolution=None, framerate=None):
        await self.open(resolution, framerate)
        return self._stream_task.response_stream

    # show/view


