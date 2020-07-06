import asyncio
from . import error, util
from gpiozero.tones import Tone
from wsmprpc import RPCStream

class Buzzer(util.StreamComponent):
    """蜂鸣器"""

    def _get_rpc(self):
        self._rpc_stream = RPCStream()
        if self._mode == 'aio':
            self._input_stream = util.AsyncStream(self._rpc_stream, encode_fn=self._encode)
        else:
            self._input_stream = util.SyncStream(util.SyncRawStream(self._rpc_stream, self._loop), encode_fn=self._encode)
        return self._rpc.play(request_stream=self._rpc_stream)

    @util.mode(force_sync=False)
    async def set_tone(self, tone, duration=None):
        """设置蜂鸣器的音调

        :param tone: 音调。可以是频率、MIDI音符代码，也可以是音高的字母表示，或者使用 |gpiozero.tones.Tone| （推荐）
        :type tone: str / int / |gpiozero.tones.Tone|
        :param duration: 持续时间（秒），默认为 `None` ，表示无限长，直到调用 :func:`quiet`
        :type duration: float

        .. |gpiozero.tones.Tone| raw:: html

            <a href='https://gpiozero.readthedocs.io/en/stable/api_tones.html' target='blank'>gpiozero.tones.Tone</a>

        """
        await self._rpc.tone(Tone(tone).frequency, duration)

    @util.mode()
    async def quiet(self):
        """静音/停止"""
        await self._close()
        await self._rpc.tone(None, None)

    @util.mode(force_sync=False)
    async def play(self, song):
        """播放一段音乐

        :param song: 要播放的音乐，
        :type song: collections.Iterable
        """
        async with self:
            for tone, delay in song:
                await self._rpc_stream.put(self._encode(tone))
                await asyncio.sleep(delay)
            await self._rpc_stream.put(None)

    @property
    def input_stream(self):
        """音调输入流
        """
        if self.closed:
            raise error.CozmarsError('Buzzer is closed')
        return self._input_stream

    def _encode(self, obj):
        return Tone(obj).frequency



