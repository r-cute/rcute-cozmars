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
        """cannot be set when device is running, otherwise an exception will be thrown"""
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, sr):
        if not self.closed:
            raise RuntimeError('Cannot set sample_rate while microphone is recording')
        self._sample_rate = sr

    @property
    def dtype(self):
        """Sampling data type, the default is `'int16'`.

        Cannot be set when device is running, otherwise an exception will be thrown
        """
        return self._dtype

    @dtype.setter
    def dtype(self, dt):
        if not self.closed:
            raise RuntimeError('Cannot set dtype while microphone is recording')
        self._dtype = dt

    @property
    def channels(self):
        """Number of channels, which is `1` and read only
        """
        return 1

    @property
    def sample_width(self):
        """How many bytes does A sample contains, corresponding to :data:`dtype`, read only """
        return util.sample_width(self.dtype)

    @property
    def block_duration(self):
        """The duration (seconds) of each sound clip in the stream, the default is `0.1`

        Cannot be set when device is running, otherwise an exception will be thrown
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
        """Volume level, 0~100, in percentage. Modification is saved even after reboot.

        It's recommanded to set 100 for microphone volume, and 50 for speaker.

        Dynamic volume modification should be done via :data:`gain`
        """
        return await (self._volume()(*args))
