from .util import Component
from . import error

class Camera(Component):
    def __init__(self, robot, resolution, framerate, q_size):
        Component.__init__(self, robot)
        self._resolution = resolution
        self._framerate = framerate
        self._q_size = q_size
        self._stream_task = None

    @property
    def closed(self):
        return not self._stream_task or self._stream_task.done()

    @property
    def framerate(self):
        return self._framerate

    @framerate.setter
    def framerate(self, framerate):
        if not self.closed:
            raise error.CozmarsError('Cannot change framerate when camera is running')
        self._framerate = framerate

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        if not self.closed:
            raise error.CozmarsError('Cannot change resolution when camera is running')
        self._resolution = resolution

    @mode()
    async def open(self, resolution=None, framerate=None):
        if resolution:
            self.resolution = resolution
        if framerate:
            self.framerate = framerate
        if self.closed:
            self._stream_task = self.rpc.cam(self.resolution[0], self.resolution[1], self.framerate, q_size=self._q_size)
            await self._stream_task.request()

    @mode()
    async def close(self):
        if not self.closed:
            self._stream_task.cancel()

    @mode()
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


