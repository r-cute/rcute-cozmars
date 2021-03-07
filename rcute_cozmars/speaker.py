import asyncio, functools, itertools, io
from. import util
from .sound_mixin import soundmixin
import numpy as np
from collections.abc import Iterable
from inspect import isasyncgen
from pydub import AudioSegment
from pydub.generators import Sine
import librosa
from pydub.playback import play

import warnings
warnings.filterwarnings('ignore', message='PySoundFile failed. Trying audioread instead.') # librosa

class Speaker(util.InputStreamComponent, soundmixin):
    """Speaker is only for Cozmars v2"""
    def __init__(self, robot):
        util.InputStreamComponent.__init__(self, robot)
        soundmixin.__init__(self, dtype='int16', sample_rate=22050, block_duration=.1, gain=25)
        self._lock = asyncio.Lock()

    def _get_rpc(self):
        return self._rpc.speaker(self._t_sr, self._t_dt, self._t_bs, self._t_vol, request_stream=self._input_stream)

    def _volume(self):
        return self._rpc.speaker_volume

    @util.mode()
    async def play(self, src, repeat=1, preload=5, **kw):
        """Playback sound

        :param src: The sound resource to be played (file/URL/data)
        :type src: str/np.ndarray/bytes/iterable/file-like obj
        :param repeat: play times, default is 1
        :type repeat: int, optional
        """
        sr = kw.get('sample_rate', self.sample_rate)
        dt = kw.get('dtype', self.dtype)
        bd = kw.get('block_duration', self.block_duration)
        vol = kw.get('volume', None)
        bs = int(bd * sr)
        if isinstance(src, str) or hasattr(src, 'read'): # for file-like obj
            sr, dt, bs, src = await asyncio.get_running_loop().run_in_executor(None, file_sr_bs_gen, src, sr, dt, bd)

        elif isinstance(src, np.ndarray):
            dt, src = np_gen(src, dt, bs)

        elif isinstance(src, bytes):
            src = raw_gen(src, dt, bs)

        # elif isinstance(src, Iterable) or isasyncgen(src):
            # if src is a sync/async iterable,
            # it must yield data blocks of length=samplerate*bypedepth
            # pass

        # else:
        #     raise TypeError(f'Unable to open {src}')

        async with self._lock:
            self._t_sr = sr # temp
            self._t_dt = dt
            self._t_bs = bs
            self._t_vol = vol
            async with self:
                count = 0
                if isinstance(src, Iterable):
                    for raw in repeat_gen(src, repeat):
                        await self._input_stream.put(raw)
                        if count < preload:
                            await asyncio.sleep(bd * .5)
                            count += bd
                        else:
                            await asyncio.sleep(bd * .95)
                # elif isasyncgen(src):
                else:
                    async for raw in src: # no repeat
                        await self._input_stream.put(raw)
                        if count < preload:
                            await asyncio.sleep(bd * .5)
                            count += bd
                        else:
                            await asyncio.sleep(bd * .95)

    @util.mode()
    async def beep(self, tones, repeat=1, tempo=120, fade=.1):
        """play a sequence of tones

        :param tones: array of tones
        :type tones: collections.Iterable
        :param tempo: playback speed, default is `120` BPM
        :type tempo: int
        :param fade: ratio of fade duration to the entire beat, 0~1, the default is 0.1
        :type fade: float
        :param repeat: play times, default is 1
        :type repeat: int, optional

        .. note::

            This API may change in the future when we come up with a more convenient API to play tones

        """
        if not 0<= fade <1:
            raise ValueError('fade out of range [0, 1)')
        # find min freq required to save bandwidth
        sr = max_freq(tones)
        if sr > 11025:
            sr = 44100
        elif sr > 800:
            sr = 22050
        else:
            sr = 16000
        aud = await asyncio.get_running_loop().run_in_executor(None, tone2audio, tones, 60000.0/tempo, fade, sr)
        await self.play(aud.raw_data+ b'\x00'*int(sr*.1), repeat=repeat, sample_rate=sr, dtype='int16')


def max_freq(tones):
    return functools.reduce(lambda r,e: max(r, max_freq(e) if isinstance(e, (list, tuple)) else util.freq(e)), tones, 0)

def tone2audio(tones, base_beat_ms, fade, sr):
    fade *= base_beat_ms
    return functools.reduce(lambda r,e: r+(tone2audio(e, base_beat_ms/2, fade, sr) if isinstance(e, (list, tuple)) else \
            (Sine(util.freq(e), sample_rate=sr).to_audio_segment(duration=base_beat_ms).append(AudioSegment.silent(duration=fade, frame_rate=sr), crossfade=fade)) if e else AudioSegment.silent(duration=base_beat_ms, frame_rate=sr)), \
        tones, AudioSegment.empty())

def file_sr_bs_gen(src, sr, dt, block_duration):
    # input recommended samplerate, dtype, and block_duration
    # return actual samplerate, blocksize and generator
    if src.startswith('http'):
        from urllib.request import urlopen
        import io
        src = io.BytesIO(urlopen(src).read())

    import soundfile as sf
    try:
        file = sf.SoundFile(src)
        assert file.samplerate <= sr
        bs = int(block_duration * file.samplerate)
        return file.samplerate, dt, bs, map(lambda b: (b if b.ndim==1 else b.mean(axis=1, dtype=dt)).tobytes(),
            file.blocks(dtype=dt, blocksize=bs, fill_value=0))

    except (AssertionError, RuntimeError):
        # librosa supports more formats than soundfile
        # down-sample if needed
        if librosa.get_samplerate(src) < sr:
            sr = None
        y, sr = librosa.load(src, sr=sr, mono=True, res_type='kaiser_fast')
        bs = int(sr * block_duration)
        dt, gen = np_gen(y, dt, bs)
        return sr, dt, bs, gen

def np_gen(data, dt, bs):
    # convert data to specified dtype
    if data.ndim >1:
        data = data.mean(axis=1, dtype=dt)
    if str(data.dtype).startswith('float') and dt.startswith('int'):
        data = (data * np.iinfo(dt).max).astype(dt)
    elif (str(data.dtype).startswith('int') and dt.startswith('float')) or\
        (str(data.dtype)=='float32' and dt=='float64'):
        dt = str(data.dtype)
    elif str(data.dtype)=='float64' and dt=='float32':
        data = data.astype('float32')
    #   data = data.astype(dt) / np.iinfo(data.dtype).max
    # elif (int8 <--> int16 <--> int32 convertion, but int8/32 is very rarely used)
    return dt, raw_gen(data.tobytes(), dt, bs)

def raw_gen(data, dt, bs):
    bs *= util.sample_width(dt)
    for i in range(0, len(data), bs):
        b = data[i: i+ bs]
        if len(b) < bs:
            b += b'\x00' * (bs-len(b))
        yield b

def repeat_gen(gen, repeat):
    if repeat == 1:
        yield from gen
    else:
        for g in itertools.tee(gen, repeat):
            yield from g
