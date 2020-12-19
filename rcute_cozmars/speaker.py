import asyncio
import inspect
from . import util
from .sound_mixin import SoundMixin
import numpy as np
import soundfile as sf
import librosa
from gpiozero.tones import Tone
from wsmprpc import RPCStream

class Speaker(util.InputStreamComponent, SoundMixin):
    """扬声器"""

    def __init__(self, robot):
        util.InputStreamComponent.__init__(self, robot)
        SoundMixin.__init__(self)

    def _get_rpc(self):
        return self._rpc.speaker(self.samplerate, self.dtype, self.block_duration, request_stream=self._input_stream)

    def _volume(self):
        return self._rpc.speaker_volume

    def _file_gen(self, src):
    # auto convert dtype/samplerate/channels
        try:
            file = sf.SoundFile(src)
            assert file.samplerate == self.sample_rate
            for b in file.blocks(dtype=self.dtype, blocksize=int(self.block_duration*file.samplerate), fill_value=0):
                yield (b if b.ndim==1 else b.mean(axis=1, dtype=self.dtype)).tobytes()
        except (AssertionError, RuntimeError):
            y, sr = librosa.load(src, sr=self.sample_rate, mono=True, res_type='kaiser_fast')
            yield from self._np_gen(y)


    def _np_gen(self, data):
    # auto convert dtype/channels
    # data must be captured in same samplerate with speaker
        blocksize = int(self.block_duration * self.sample_rate)
        if data.ndim >1:
            data = data.mean(axis=1, dtype=self.dtype)
        for i in range(0, len(data), blocksize):
            b = data[i: i+ blocksize]
            if b.shape[0] < blocksize:
                b = np.append(b, np.zeros((blocksize-b.shape[0],), dtype=b.dtype))
            if str(b.dtype).startswith('float') and self.dtype.startswith('int'):
                b = (b * np.iinfo(self.dtype).max).astype(self.dtype)
            elif str(b.dtype).startswith('int') and self.dtype.startswith('float'):
                b = b.astype(self.dtype) / np.iinfo(b.dtype).max
            yield b.tobytes()

    def _raw_gen(self, data):
    # data must be captured in the same samplerate/dtype/channel with speaker
        blocksize = int(self.block_duration * self.sample_rate * self.sample_width)
        for i in range(0, len(data), blocksize):
            b = data[i: i+ blocksize]
            if len(b) < blocksize:
                b += b'\x00' * (blocksize-len(b))
            yield b

    @util.mode()
    async def play(self, src):
        """播放

        :param src: 要播放的声音资源（文件/网址/数据）
        :type src: src/np.ndarray/bytes/generator/file-like obj
        """
        if isinstance(src, str):
            if src.startswith('http'):
                from urllib.request import urlopen
                import io
                src = io.BytesIO(urlopen(src).read())
            src = self._file_gen(src)

        elif hasattr(src, 'read'):
            src = self._file_gen(src)

        elif isinstance(src, np.ndarray):
            src = self._np_gen(src)

        elif isinstance(src, bytes):
            src = self._raw_gen(src)

        elif inspect.isgenerator(src):
            async with self:
                for raw in src:
                    await self._input_stream.put(raw)
                    await asyncio.sleep(self.block_duration * .9)
        if inspect.isasyncgen(src):
            async with self:
                async for raw in src:
                    await self._input_stream.put(raw)
                    await asyncio.sleep(self.block_duration * .9)
        else:
            raise TypeError(f'Unable to open {src}')
