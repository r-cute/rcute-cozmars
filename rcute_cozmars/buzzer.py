import asyncio
from . import util
from gpiozero.tones import Tone
from wsmprpc import RPCStream


class Buzzer(util.StreamComponent):
    """蜂鸣器

    蜂鸣器能以不同的频率振动，从而发出不同的 `音调`。

    .. |Tone| raw:: html

        <a href='https://gpiozero.readthedocs.io/en/stable/api_tones.html' target='blank'>gpiozero.tones.Tone</a>

    .. note::

        这里所说的 `音调` ，在程序中可以用不同的数据类型表示。

        比如 C 大调 do re me 中的 do 音，音乐记号是 `'C4'` ，频率是 440.0 Hz，MIDI 代码是 #69，那么，`'C4'` 、 `440.0` 和 `69` 都可以用来表示这个音调，也可以用 |Tone| 对象来表示

        用 `None` 或 `0` 表示静音

    """

    def __init__(self, robot):
        util.StreamComponent.__init__(self, robot)
        self._tone = None

    def _get_rpc(self):
        self._input_stream = RPCStream()
        return self._rpc.play(request_stream=self._input_stream)

    @util.mode(property_type='setter')
    async def tone(self, *args):
        """蜂鸣器当前的 `音调`
        """
        if args:
            await self.set_tone(args[0], aio_mode=True)
        else:
            return self._tone

    @util.mode(force_sync=False)
    async def set_tone(self, tone, duration=None):
        """设置蜂鸣器的 `音调`

        :param tone: `音调`
        :type tone: str / int / |Tone|
        :param duration: 持续时间（秒），默认为 `None` ，表示无限长，直到调用 :func:`quiet`
        :type duration: float

        """
        if self.closed:
            t = self._encode(tone)
            await self._rpc.tone(t.frequency, duration)
            self._tone = t
        else:
            raise RuntimeError('Cannot set tone while buzzer is playing')

    @util.mode()
    async def quiet(self):
        """静音/停止"""
        await self._close()
        await self._rpc.tone(None, None)
        self._tone = None

    async def _play_one_tone(self, tone, delay, duty_cycle):
        if isinstance(tone, tuple):
            for t in tone:
                await self._play_one_tone(t, delay/2, duty_cycle)
        else:
            await self._input_stream.put(self._encode(tone))
            await asyncio.sleep(delay* duty_cycle)
            if duty_cycle != 1:
                await self._input_stream.put(None)
                await asyncio.sleep(delay* (1-duty_cycle))

    @util.mode(force_sync=False)
    async def play(self, song, tempo=120, duty_cycle=.9):
        """播放一段音乐

        :param song: 要播放的音乐
        :type song: collections.Iterable
        :param tempo: 播放速度，BPM，默认是 `120` 拍/分钟
        :type tempo: int
        :param duty_cycle: 占空比，即音节播放时间与整个音节的时间的比值，0~1，默认是 `0.9`
        :type duty_cycle: float

        .. warning::

            这个 API 将来可能会改变，我们还在探索更方便播放音乐的 API

        """

        if not 0< duty_cycle <=1:
            raise ValueError('duty_cycle out of range (0, 1]')
        delay = 60 / tempo
        async with self:
            for tone in song:
                await self._play_one_tone(tone, delay, duty_cycle)
            await self._input_stream.put(None)

    '''
    @property
    def input_stream(self):
        """蜂鸣器输入流

        获取输入流必须在蜂鸣器打开之后，否则抛出异常
        """
        if self.closed:
            raise RuntimeError('Buzzer is closed')
        return self._input_stream

    @property
    def raw_input_stream(self):
        return self.input_stream._raw_stream
    '''



    def _encode(self, obj):
        return Tone(obj).frequency if obj else None



