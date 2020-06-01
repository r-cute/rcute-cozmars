from .util import Component
from . import error

class Camera(Component):
    def __init__(self, robot, resolution, framerate):
        Component.__init__(self, robot)
        self._resolution = resolution
        self._framerate = framerate
        self._stream_task = None

    @property
    def on(self):
        return self._stream_task and not self._stream_task.done()

    @property
    def framerate(self):
        return self._framerate

    @framerate.setter
    def framerate(self, framerate):
        if self.on:
            raise error.CozmarsError('Cannot set framerate when camera is on')
        self._framerate = framerate

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        if self.on:
            raise error.CozmarsError('Cannot set resolution when camera is on')
        self._resolution = resolution

    async def start(self):
        if not self.on:
            self._stream_task = self.rpc.cam(self.resolution[0], self.resolution[1], self.framerate)
        await self._stream_task

    async def frames(self):
        if not self.on:
            await self.start()
        return self._stream_task.response_stream

    async def release(self):
        if self.on:
            self._stream_task.cancel()
        await self._stream_task




