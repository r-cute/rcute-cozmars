import asyncio
from . import util
from gpiozero.tones import Tone
from wsmprpc import RPCStream


class Buzzer(util.StreamComponent):
    """蜂鸣器

    .. |gpiozero.tones.Tone| raw:: html

        <a href='https://gpiozero.readthedocs.io/en/stable/api_tones.html' target='blank'>gpiozero.tones.Tone</a>

    """

    def __init__(self, robot):
        util.StreamComponent.__init__(self, robot)
        self._tone = None

    def _get_rpc(self):
        self._rpc_stream = RPCStream()
        if self._mode == 'aio':
            self._input_stream = util.AsyncStream(self._rpc_stream, encode_fn=self._encode)
        else:
            self._input_stream = util.SyncStream(util.SyncRawStream(self._rpc_stream, self._loop), encode_fn=self._encode)
        return self._rpc.play(request_stream=self._rpc_stream)

    @util.mode(property_type='setter')
    async def tone(self, *args):
        """蜂鸣器当前的 `音调`

        `音调` 在程序中可以用频率、MIDI音符代码、或者音高字符表示，也可以使用 |gpiozero.tones.Tone| （推荐），`None` 则表示静音
        """
        if args:
            await self._set_tone(args[0])
        else:
            return self._tone

    @util.mode(force_sync=False)
    async def set_tone(self, tone, duration=None):
        """设置蜂鸣器的音调

        :param tone: 音调
        :type tone: str / int / |gpiozero.tones.Tone|
        :param duration: 持续时间（秒），默认为 `None` ，表示无限长，直到调用 :func:`quiet`
        :type duration: float

        """
        return await self._set_tone(tone, duration)

    async def _set_tone(self, tone, duration=None):
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

    @util.mode(force_sync=False)
    async def play(self, song):
        """播放一段音乐

        :param song: 要播放的音乐，由声音组成的数组，每个元素是一个音调和时间组成的 `tuple`
        :type song: collections.Iterable
        """
        async with self:
            for tone, delay in song:
                t = self._encode(tone)
                await self._rpc_stream.put(t)
                await asyncio.sleep(delay)
                self._tone = t
            await self._rpc_stream.put(None)
            self._tone = None

    @property
    def input_stream(self):
        """蜂鸣器输入流

        获取输入流必须在蜂鸣器打开之后，否则抛出异常
        """
        if self.closed:
            raise RuntimeError('Buzzer is closed')
        return self._input_stream

    def _encode(self, obj):
        return Tone(obj).frequency if obj else None



