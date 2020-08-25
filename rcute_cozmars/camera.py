from . import util
import numpy as np
import cv2

class Camera(util.OutputStreamComponent):
    """摄像头
    """
    def __init__(self, robot, resolution=(480,360), frame_rate=3, q_size=1):
        util.OutputStreamComponent.__init__(self, robot)
        self._q_size = q_size
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

    def _decode(self, data):
        return cv2.flip(cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR), -1)

    def _get_rpc(self):
        w, h = self.resolution
        return self._rpc.camera(w, h, self.frame_rate, q_size=self._q_size)

    '''
    @util.mode()
    async def capture(self, options):
        """拍照

        :param options: 拍照的参数
        :type options: dict
        :return: 照片
        :rtype: numpy.ndarray
        """
        if self.closed:
            return await self._rpc.capture(options)
        else:
            raise RuntimeError('Cannot take a photo while camera is streaming video')
    '''

    '''
    @property
    def raw_output_stream(self):
        """摄像头的二进制数据流，与 :data:`output_stream` 相对

        流中的每一帧数据都是一张图片 jpeg 格式的二进制数据

        读取数据流必须摄像头打开之后，否则抛出异常
        """
        return self.output_stream._raw_stream

    @property
    def output_stream(self):
        """ 摄像头的数据流，将 :data:`raw_output_stream` 中的每一帧二进制数据封装为 `numpy.ndarray` 类型

        数据流中的每一帧是一张图片

        读取数据流必须摄像头打开之后，否则抛出异常
        """
        if self.closed:
            raise RuntimeError(f'{self.__class__.__name__} is closed')
        return self._output_stream

    '''