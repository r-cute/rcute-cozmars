import asyncio
from. import util


# import numpy as np
from pydub import AudioSegment
class MicrophoneMultiplexOutputStream(util.MultiplexOutputStream):
    def __init__(self, component):
        util.MultiplexOutputStream.__init__(self, component)

    def force_put_nowait(self, o):
        if not isinstance(o, Exception):
            # o = (np.frombuffer(o, dtype=self._dtype) * self._component.gain).tobytes()
            o = AudioSegment(data=o, sample_width=self._component.sample_width, frame_rate=self._component.sample_rate, channels=self._component.channels)
            o = o.apply_gain(self._component.gain)
        util.MultiplexOutputStream.force_put_nowait(self, o)

class Microphone(util.MultiplexOutputStreamComponent):
    """Microphone"""
    def __init__(self, robot, gain=25, sample_rate=16000, dtype='int16', block_duration=0.1, q_size=1):
        util.MultiplexOutputStreamComponent.__init__(self, robot, q_size, MicrophoneMultiplexOutputStream(self))
        self._sample_rate = sample_rate
        self._block_duration = block_duration
        self._dtype = dtype
        self._gain = gain

    def _get_rpc(self):
        self._multiplex_output_stream._dtype = self._dtype
        return self._rpc.microphone(self.sample_rate, self.dtype, self.block_duration, response_stream=self._multiplex_output_stream)

    @property
    def sample_rate(self):
        """ The sampling rate of the microphone, the default is `16000`, it is not recommended to modify

        The microphone cannot be set after it is turned on, otherwise an exception will be thrown
        """
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, sr):
        if not self.closed:
            raise RuntimeError('Cannot set sample_rate while microphone is recording')
        self._sample_rate = sr

    @property
    def dtype(self):
        """ The data type of microphone sampling, such as `'int8'` or `'float32'`, etc. The default is `'int16'`, it is not recommended to modify

        The microphone cannot be set after it is turned on, otherwise an exception will be thrown
        """
        return self._dtype

    @dtype.setter
    def dtype(self, dt):
        if not self.closed:
            raise RuntimeError('Cannot set dtype while microphone is recording')
        self._dtype = dt

    @property
    def channels(self):
        """The number of microphone channels, the default is `1`, read only
        """
        return 1

    @property
    def sample_width(self):
        """A sample contains several bytes, corresponding to :data:`dtype`, read only 
        """
        return util.sample_width(self.dtype)

    @property
    def block_duration(self):
        """The duration of each frame of sound clip in the stream (seconds), the default is `0.1`, it is not recommended to modify
        The microphone cannot be set after it is turned on, otherwise an exception will be thrown
        """
        return self._block_duration

    @block_duration.setter
    def block_duration(self, fd):
        if not self.closed:
            raise RuntimeError('Cannot set block_duration while microphone is recording')
        self._block_duration = fd

    @util.mode(property_type='setter')
    async def volume(self, *args):
        """ The volume of the microphone, 0~100, in percent system, it will be automatically saved after setting, and it will still be effective after restarting, generally set to 100%, it is not recommended to modify

        To adjust the volume, you should modify the volume gain

        The microphone cannot be set after it is turned on, otherwise an exception will be thrown
        """
        if args and not self.closed:
            raise RuntimeError('Cannot set volume while microphone is recording')
        return await self._rpc.microphone_volume(*args)

    @property
    def gain(self):
        """Volume gain (dBFS), default is 25"""
        return self._gain

    @gain.setter
    def gain(self, g):
        self._gain = g

    # def get_buffer(self):
    #     b = util.MultiplexOutputStreamComponent.get_buffer(self)
    #     b.sample_width = self.sample_width
    #     b.sample_rate = self.sample_rate
    #     b.block_duration = self.block_duration
    #     b.channels = self.channels
    #     return b
