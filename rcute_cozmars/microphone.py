import asyncio
from . import util
from .sound_mixin import SoundMixin

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

class Microphone(util.MultiplexOutputStreamComponent, SoundMixin):
    """麦克风"""
    def __init__(self, robot, gain=25, sample_rate=16000, dtype='int16', block_duration=0.1, q_size=1):
        util.MultiplexOutputStreamComponent.__init__(self, robot, q_size, MicrophoneMultiplexOutputStream(self))
        SoundMixin.__init__(self)

    def _get_rpc(self):
        self._multiplex_output_stream._dtype = self._dtype
        return self._rpc.microphone(self.sample_rate, self.dtype, self.block_duration, response_stream=self._multiplex_output_stream)

    def _volume(self):
        return self._rpc.microphone_volume