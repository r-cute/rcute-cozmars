import asyncio
from . import util
from .sound_mixin import soundmixin

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

class Microphone(util.MultiplexOutputStreamComponent, soundmixin):
    def __init__(self, robot, q_size=1):
        util.MultiplexOutputStreamComponent.__init__(self, robot, q_size, MicrophoneMultiplexOutputStream(self))
        soundmixin.__init__(self, dtype='int16', sample_rate=16000, block_duration=.1, gain=25)

    def _get_rpc(self):
        self._multiplex_output_stream._dtype = self._dtype
        return self._rpc.microphone(self.sample_rate, self.dtype, int(self.block_duration*self.sample_rate), response_stream=self._multiplex_output_stream)

    def _volume(self):
        return self._rpc.microphone_volume