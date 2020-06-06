from . import error, util

class Camera(util.OutputStreamComponent):
    def __init__(self, robot, resolution, framerate, q_size):
        util.OutputStreamComponent.__init__(self, robot)
        self._q_size = q_size
        self._framerate = framerate
        self._resolution = resolution

    @property
    def resolution(self):
        return self._resolution

    @property
    def framerate(self):
        return self._framerate

    @resolution.setter
    def resolution(self, res):
        if not self.closed:
            raise error.CozmarsError('Cannot set resolution while camera is running')
        self.resolution = res

    @framerate.setter
    def framerate(self, fr):
        if not self.closed:
            raise error.CozmarsError('Cannot set framerate while camera is running')
        self.framerate = fr


    def _get_rpc(self):
        w, h = self.resolution
        return self.rpc.camera(w, h, self.framerate, q_size=self._q_size)

    @util.mode()
    async def capture(self, options):
        if self.closed:
            return await self.rpc.capture(options)
        else:
            raise error.CozmarsError('Cannot take a photo while camera is streaming video')


