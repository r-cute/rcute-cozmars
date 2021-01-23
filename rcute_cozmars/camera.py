from . import util
import numpy as np
import cv2

class CameraMultiplexOutputStream(util.MultiplexOutputStream):
    def force_put_nowait(self, o):
        if not isinstance(o, Exception):
            o = cv2.flip(cv2.imdecode(np.frombuffer(o, dtype=np.uint8), cv2.IMREAD_COLOR), -1)
        util.MultiplexOutputStream.force_put_nowait(self, o)

class Camera(util.MultiplexOutputStreamComponent):
    """camera
    """
    def __init__(self, robot, resolution=(480,360), frame_rate=3, q_size=1):
        util.MultiplexOutputStreamComponent.__init__(self, robot, q_size, CameraMultiplexOutputStream(self))
        self._frame_rate = frame_rate
        self._resolution = resolution
        self._standby = False

    @property
    def resolution(self):
        """The resolution of the camera, the default is `(480, 360)`

        The resolution cannot be modified after the camera has been opened, otherwise an exception will be thrown
        """
        return self._resolution

    @property
    def frame_rate(self):
        """The frame rate of camera recording, namely FPS, default is `3`

        The frame rate cannot be modified after the camera has been opened, otherwise an exception will be thrown
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
        if self._standby:
            raise RuntimeError('Cannot get video stream buffer while in capture standby mode')
        w, h = self.resolution
        return self._rpc.camera(w, h, self.frame_rate, response_stream=self._multiplex_output_stream)

    @util.mode()
    async def capture(self, output=None, **options):
        """Photo

        :param output: Output, if it is a file path or an object with the :meth:`write` method, it will be saved to the specified location. Default is `None`
        :type output: str/writable, optional
        :param options:
            * delay - The default is 1, which means the camera is turned on for 1 second before taking pictures. Give the camera more time to warm up and focus, and the image quality may be better
            * standby - the default is False, if it is set to True, the camera will not turn off after taking pictures, which is convenient for continuous taking pictures. When taking photos in standby mode continuously, delay defaults to 0
            * For other optional parameters, please refer to `PiCamera.capture() <https://picamera.readthedocs.io/en/release-1.13/api_camera.html#picamera.PiCamera.capture>`_
        :type options: optional
        :return: If :data:`output` is None, return a numpy.ndarray object
        :raises RuntimeError: When the camera is transmitting video, it can’t take pictures; it can’t transmit video when in standby mode.
        """
        if not self.closed:
            raise RuntimeError('Cannot capture image while camera is streaming video')
        op = {'delay': 0 if self._standby else 1, 'resize': self.resolution}
        op.update(options)
        if'format' not in op:
            op.update({'format': output.split('.')[-1] if isinstance(output, str) else 'jpeg'})
        self._standby = op.get('standby', False)
        data = await self._rpc.capture(op)
        if output is None:
            return cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
        elif isinstance(output, str):
            with open(output, 'wb') as file:
                file.write(data)
        else:
            output.write(data)
    