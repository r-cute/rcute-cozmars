from . import util

class soundmixin:

    def __init__(self, dtype, sample_rate, block_duration, gain):
        self._dtype = dtype
        self._sample_rate = sample_rate
        self._block_duration = block_duration
        self._dtype = dtype
        self._gain = gain

    @property
    def sample_rate(self):
        """采样率

        设备已经打开之后不能进行设置，否则抛出异常
        """
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, sr):
        if not self.closed:
            raise RuntimeError('Cannot set sample_rate while microphone is recording')
        self._sample_rate = sr

    @property
    def dtype(self):
        """采样的数据类型，如 `'int8'` 或 `'float32'` 等，默认是 `'int16'` ，不建议修改

        设备已经打开之后不能进行设置，否则抛出异常
        """
        return self._dtype

    @dtype.setter
    def dtype(self, dt):
        if not self.closed:
            raise RuntimeError('Cannot set dtype while microphone is recording')
        self._dtype = dt

    @property
    def channels(self):
        """声道数，默认是 `1` ，只读
        """
        return 1

    @property
    def sample_width(self):
        """一个采样包含几个字节，与 :data:`dtype` 对应，只读"""
        return util.sample_width(self.dtype)

    @property
    def block_duration(self):
        """流中每一帧声音片段持续的时间（秒），默认是 `0.1`

        设备已经打开之后不能进行设置，否则抛出异常
        """
        return self._block_duration

    @block_duration.setter
    def block_duration(self, fd):
        if not self.closed:
            raise RuntimeError('Cannot set block_duration while device is streaming')
        self._block_duration = fd

    @property
    def gain(self):
        """音量增益(dBFS)"""
        return self._gain

    @gain.setter
    def gain(self, g):
        self._gain = g

    @util.mode(property_type='setter')
    async def volume(self, *args):
        """音量大小，0~100，百分制，设置以后会自动保存，重启后依然有效

        麦克风音量推荐设置成 100%，然后可以通过音量增益进一步增大

        扬声器音量推荐设成 50%
        """
        return await (self._volume()(*args))