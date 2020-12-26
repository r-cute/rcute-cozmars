import asyncio, inspect, functools, re
from . import util
from .sound_mixin import SoundMixin
import numpy as np
from collections.abc import Iterable
import soundfile as sf, wave, io
from pydub import AudioSegment
from pydub.generators import Sine
from gpiozero.tones import Tone


class Speaker(util.InputStreamComponent, SoundMixin):
    """扬声器"""

    def __init__(self, robot):
        util.InputStreamComponent.__init__(self, robot)
        SoundMixin.__init__(self)
        self._lock = asyncio.Lock()

    def _get_rpc(self):
        rpc = self._rpc.speaker(self._t_sr or self.samplerate, self._t_dt or self.dtype, self.block_duration, request_stream=self._input_stream)
        self._t_sr = self._t_dt = None
        return rpc

    def _volume(self):
        return self._rpc.speaker_volume

    async def _file_gen(self, src):
    # auto convert dtype/samplerate/channels
        try:
            file = sf.SoundFile(src)
            assert file.samplerate <= self.sample_rate
            return file.samplerate, map(lambda b:(b if b.ndim==1 else b.mean(axis=1, dtype=self.dtype)).tobytes()\
                for b in file.blocks(dtype=self.dtype, blocksize=int(self.block_duration*file.samplerate), fill_value=0))

        except (AssertionError, RuntimeError):
            import functools, librosa # librosa supports more formats than soundfile
            # down-sample if needed
            sr = self.sample_rate if librosa.get_samplerate(src)> self.sample_rate else None
            load = functools.partial(librosa.load, src, sr=sr, mono=True, res_type='kaiser_fast')
            y, sr = await asyncio.get_running_loop().run_in_executor(None, load)
            return sr, self._np_gen(y)


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

    def _repeat_gen(self, gen, repeat=1):
        while repeat != 0:
            yield from gen
            repeat -= 1

    @util.mode()
    async def play(self, src, repeat=1, **kw):
        """播放

        :param src: 要播放的声音资源（文件/网址/数据）
        :type src: str/np.ndarray/bytes/iterable/file-like obj
        :param repeat: 播放次数，默认为 1，-1 表示不断循环
        :type repeat: int, optional
        """
        sr = None
        if isinstance(src, str):
            if src.startswith('http'):
                from urllib.request import urlopen
                import io
                src = io.BytesIO(urlopen(src).read())
            sr, src = await self._file_gen(src)

        elif hasattr(src, 'read'):
            sr, src = self._file_gen(src)

        elif isinstance(src, np.ndarray):
            src = self._np_gen(src)

        elif isinstance(src, bytes):
            src = self._raw_gen(src)

        elif isinstance(src, Iterable):
            async with self._lock:
                self._t_sr = kw.get('sample_rate', sr)
                self._t_dt = kw.get('dtype')
                async with self:
                    for raw in self._repeat_gen(src, repeat):
                        await self._input_stream.put(raw)
                        await asyncio.sleep(self.block_duration * .95)
        # if inspect.isasyncgen(src):
        #     async with self._lock:
        #         self._t_sr = kw.get('sample_rate', sr)
        #         self._t_dt = kw.get('dtype')
        #         async with self:
        #             async for raw in src:
        #                 await self._input_stream.put(raw)
        #                 await asyncio.sleep(self.block_duration * .95)
        else:
            raise TypeError(f'Unable to open {src}')

    @util.mode()
    async def say(self, txt, **options):
        """说话

        :param txt: 要说的字符串
        :type txt: str
        :param options:
            * voice 语言
            * volume 音量
            * pitch 音调
            * speed 语速
            * word_gap 字间停顿

            见 `py-espeak-ng <https://github.com/gooofy/py-espeak-ng>`_
        :type options: optional
        """
        if not hasattr(self, '_esng'):
            from espeakng import ESpeakNG
            self._esng = ESpeakNG()
        op = {voice: 'zh' if re.findall(r'[\u4e00-\u9fff]+', txt) else 'en'}
        op.update(options)
        for k, v in op.items():
            setattr(self._esng, k, v)
        wav_data = await asyncio.get_running_loop().run_in_executor(None, self._esng.synth_wav, txt)
        with wave.open(io.BytesIO(wav_data)) as f:
            await self.play(f.readframes(f.getnframes()), sample_rate=f.getframerate(), dtype='int16')

    @util.mode()
    async def beep(self, tones, repeat=1, tempo=120, duty_cycle=.9):
        """哼一段曲子

        :param tones: 一串音调组成的曲子
        :type tones: collections.Iterable
        :param tempo: 播放速度，BPM，默认是 `120` 拍/分钟
        :type tempo: int
        :param duty_cycle: 占空比，即音节播放时间与整个音节的时间的比值，0~1，默认是 `0.9`
        :type duty_cycle: float
        :param repeat: 播放次数，默认为 1。-1 表示不断连续播放
        :type repeat: int, optional

        .. warning::

            这个 API 将来可能会改变，我们还在探索更方便播放音乐的 API

        """
        if not 0< duty_cycle <=1:
            raise ValueError('duty_cycle out of range (0, 1]')
        sr = _max_freq(tones)
        if sr > 11025:
            sr = 44100
        elif sr > 800:
            sr = 22050
        else:
            sr = 16000
        aud = await asyncio.get_running_loop().run_in_executor(None, _tone2audio, 1000.0/tempo, duty_cycle, sr)
        await self.play(aud.raw_data, repeat=repeat, sample_rate=sr, dtype='int16')


def _max_freq(self, tones):
    return functools.reduce(lambda r,e: max(r, _max_freq(e) if isinstance(e, (list, tuple)) else Tone(e).frequency), tones, 0)

def _tone2audio(tones, base_beat_ms, duty_cycle, sr):
    duty = base_beat_ms * duty_cycle
    empty = base_beat_ms - duty
    return functools.reduce(lambda r,e: r+(_tone2audio(e, base_beat_ms/2, duty_cycle, sr) if isinstance(e, (list, tuple)) else \
            Sine(sample_rate=sr, duration=duty, freq=Tone(e).frequency).to_audio_segment().append(AudioSegment.silent(duration=empty, frame_rate=sr), crossfade=empty/2)), \
        tones, AudioSegment.empty())
