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
        """Sampling Rate

        The device cannot be set after it has been turned on, otherwise an exception will be thrown
        """
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, sr):
        if not self.closed:
            raise RuntimeError('Cannot set sample_rate while microphone is recording')
        self._sample_rate = sr

    @property
    def dtype(self):
        """Sampling data type, such as `'int8'` or `'float32'` etc. The default is `'int16'`, it is not recommended to modify

        The device cannot be set after it has been turned on, otherwise an exception will be thrown
        """
        return self._dtype

    @dtype.setter
    def dtype(self, dt):
        if not self.closed:
            raise RuntimeError('Cannot set dtype while microphone is recording')
        self._dtype = dt

    @property
    def channels(self):
        """Number of channels, default is `1`, read only
        """
        return 1

    @property
    def sample_width(self):
        """A sample contains several bytes, corresponding to :data:`dtype`, read only """
        return util.sample_width(self.dtype)

    @property
    def block_duration(self):
        """The duration of each frame of sound clip in the stream (seconds), the default is `0.1`

        The device cannot be set after it has been turned on, otherwise an exception will be thrown
        """
        return self._block_duration

    @block_duration.setter
    def block_duration(self, fd):
        if not self.closed:
            raise RuntimeError('Cannot set block_duration while device is streaming')
        self._block_duration = fd

    @property
    def gain(self):
        """Volume Gain (dBFS)"""
        return self._gain

    @gain.setter
    def gain(self, g):
        self._gain = g

    @util.mode(property_type='setter')
    async def volume(self, *args):
        """Volume level, 0~100, percentage system, the setting will be automatically saved after the setting, and it will still be valid after restarting

        The microphone volume is recommended to be set to 100%, and then it can be further increased by volume gain

        The speaker volume is recommended to be set to 50%
        """
        return await (self._volume()(*args))
