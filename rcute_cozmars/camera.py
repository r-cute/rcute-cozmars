from . import util
import numpy as np
import cv2

class CameraMultiplexOutputStream(util.MultiplexOutputStream):
    def force_put_nowait(self, o):
        if not isinstance(o, Exception):
            o = cv2.flip(cv2.imdecode(np.frombuffer(o, dtype=np.uint8), cv2.IMREAD_COLOR), -1)
        util.MultiplexOutputStream.force_put_nowait(self, o)

class Camera(util.MultiplexOutputStreamComponent):
    """摄像头
    """
    def __init__(self, robot, resolution=(480,360), frame_rate=3, q_size=1):
        util.MultiplexOutputStreamComponent.__init__(self, robot, q_size, CameraMultiplexOutputStream(self))
        self._frame_rate = frame_rate
        self._resolution = resolution

    @property
    def resolution(self):
        """摄像头的分辨率，默认是 `(480, 360)`

        摄像头已经打开之后不能修改分辨率，否则抛出异常
        """
        return self._resolution

    @property
    def frame_rate(self):
        """摄像头录像的帧率，即 FPS，默认是 `3`

        摄像头已经打开之后不能修改帧率，否则抛出异常
        """
        return self._frame_rate

    @resolution.setter
    def resolution(self, res):
        if not self.closed:
            raise RuntimeError('Cannot set resolution while camera is running')
        self._resolution = res

    @frame_rate.setter
    def frame_rate(self, fr):
        if not self.closed:
            raise RuntimeError('Cannot set frame_rate while camera is running')
        self._frame_rate = fr

    def _get_rpc(self):
        w, h = self.resolution
        return self._rpc.camera(w, h, self.frame_rate, response_stream=self._multiplex_output_stream)

