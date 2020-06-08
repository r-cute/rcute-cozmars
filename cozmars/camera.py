from . import error, util
import numpy as np
import cv2

class CameraOutputStream(util.SyncAsyncRPCStream):
    def _decode(self, data):
        return cv2.flip(cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR), -1)

class Camera(util.StreamComponent):
    def __init__(self, robot, resolution, framerate, q_size):
        util.StreamComponent.__init__(self, robot)
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
        rpc = self.rpc.camera(w, h, self.framerate, q_size=self._q_size)
        self._output_stream = CameraOutputStream(rpc.response_stream, None if self._mode=='aio' else self._loop)
        return rpc

    @util.mode()
    async def capture(self, options):
        if self.closed:
            return await self.rpc.capture(options)
        else:
            raise error.CozmarsError('Cannot take a photo while camera is streaming video')

    @property
    def output_stream(self):
        if self.closed:
            raise error.CozmarsError('Camera is closed')
        return self._output_stream