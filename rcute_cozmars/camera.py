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

    @util.mode()
    async def capture(self, output=None, **options):
        """拍照

        :param output: 输出，如果是文件路径，或者是带有 :meth:`write` 方法的对象，则会被保存到指定位置。默认为 `None`
        :type output: str/writable, optional
        :return: 如果不设置 :data:`output`，则返回一个 numpy.ndarray 对象
        :raises RuntimeError: 摄像头正在传输视频是不能拍照

        options:

        delay -- 默认为 1， 即摄像头开启 1 秒后再拍照，多给摄像头一点时间预热和对焦，图像质量可能更好

        其他可选参数参考 `PiCamera.capture() <https://picamera.readthedocs.io/en/release-1.13/api_camera.html#picamera.PiCamera.capture>`_
        """
        if not self.closed:
            raise RuntimeError('Cannot capture image while camera is streaming video')
        op = {'delay': 1, 'resize': self.resolution}
        op.update(options)
        if 'format' not in op:
            op.update({'format': output.split('.')[-1] if isinstance(output, str) else 'jpeg'})
        data = await self._rpc.capture(op)
        if output is None:
            return cv2.imdecode(np.frombuffer(o, dtype=np.uint8), cv2.IMREAD_COLOR)
        elif isinstance(output, str):
            with open(output, 'wb') as file:
                file.write(data)
        else:
            output.write(data)

