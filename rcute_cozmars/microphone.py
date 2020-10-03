import asyncio
from . import util

'''
import numpy as np
class MicrophoneMultiplexOutputStream(util.MultiplexOutputStream):
    def force_put_nowait(self, o):
        if not isinstance(o, Exception):
            o = np.frombuffer(o, dtype=self._dtype)
        util.MultiplexOutputStream.force_put_nowait(self, o)
'''

class Microphone(util.MultiplexOutputStreamComponent):
    """麦克风"""
    def __init__(self, robot, sample_rate=16000, dtype='int16', frame_duration=.1, q_size=5):
        util.MultiplexOutputStreamComponent.__init__(self, robot, q_size, util.MultiplexOutputStream(self))
        self._sample_rate = sample_rate
        self._frame_duration = frame_duration
        self._dtype = dtype

    def _get_rpc(self):
        self._multiplex_output_stream._dtype = self._dtype
        return self._rpc.microphone(self.sample_rate, self.dtype, self.frame_duration, response_stream=self._multiplex_output_stream)

    @property
    def sample_rate(self):
        """麦克风的采样率，默认是 `16000` ，不建议修改

        麦克风已经打开之后不能进行设置，否则抛出异常
        """
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, sr):
        if not self.closed:
            raise RuntimeError('Cannot set sample_rate while microphone is recording')
        self._sample_rate = sr

    @property
    def dtype(self):
        """麦克风采样的数据类型，默认是 `'int16'` ，不建议修改

        也可以设置为 `'int8'` 或 `'float32'`

        麦克风已经打开之后不能进行设置，否则抛出异常
        """
        return self._dtype

    @dtype.setter
    def dtype(self, dt):
        if not self.closed:
            raise RuntimeError('Cannot set dtype while microphone is recording')
        self._dtype = dt

    @property
    def channels(self):
        """麦克风的声道数，默认是 `1` ，只读
        """
        return 1

    @property
    def sample_width(self):
        """一个采样包含几个字节，与 :data:`dtype` 对应，只读"""
        return {'int16':2, 'float32':4, 'int8':1}[self.dtype]

    @property
    def frame_duration(self):
        """流中每一帧声音片段持续的时间（秒），默认是 `0.1` ，不建议修改

        麦克风已经打开之后不能进行设置，否则抛出异常
        """
        return self._frame_duration

    @frame_duration.setter
    def frame_duration(self, fd):
        if not self.closed:
            raise RuntimeError('Cannot set frame_duration while microphone is recording')
        self._frame_duration = fd

    @util.mode(property_type='setter')
    async def volumn(self, *args):
        """麦克风的音量大小，0~100，百分制，设置以后会自动保存，重启后依然有效

        麦克风已经打开之后不能进行设置，否则抛出异常
        """
        if args and not self.closed:
            raise RuntimeError('Cannot set volumn while microphone is recording')
        return await self._rpc.microphone_volumn(*args)

