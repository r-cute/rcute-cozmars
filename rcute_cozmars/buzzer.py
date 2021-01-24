import asyncio
from . import util
from gpiozero.tones import Tone
# from wsmprpc import RPCStream


class Buzzer(util.InputStreamComponent):
    """Buzzer is only for Cozmars v1

    The buzzer vibrates at different frequencies to emit different `tones`.

    .. |Tone| raw:: html

        <a href='https://gpiozero.readthedocs.io/en/stable/api_tones.html' target='blank'>gpiozero.tones.Tone</a>

    .. note::

        A `tone` is represented by different data types in program.

        For example, the "do" sound in C major, its music symbol is `'C4'`, the frequency is 440.0 Hz, and the MIDI code is #69, so, `'C4'`, `440.0` and `69` can all be used To represent this tone, you can also use the |Tone| object.

        Use `None` or `0` to indicate mute

    """

    def __init__(self, robot):
        util.InputStreamComponent.__init__(self, robot)
        self._tone = None

    def _get_rpc(self):
        # self._input_stream = RPCStream()
        return self._rpc.play(request_stream=self._input_stream)

    @util.mode(property_type='setter')
    async def tone(self, *args):
        """The current `tone` the buzzer is playing
        """
        if args:
            await self.set_tone(args[0])
        else:
            return self._tone

    @util.mode(force_sync=False)
    async def set_tone(self, tone, duration=None):
        """

        :param tone: `tone`
        :type tone: str / int / |Tone|
        :param duration: duration (seconds), default is `None`, which means non-stop, until :func:`quiet` is called
        :type duration: float

        """
        if self.closed:
            self._tone, freq = self._encode(tone)
            await self._rpc.tone(freq, duration)
        else:
            raise RuntimeError('Cannot set tone while buzzer is playing')

    @util.mode()
    async def quiet(self):
        """Mute/Stop"""
        await self._close()
        await self._rpc.tone(None, None)
        self._tone = None

    async def _play_one_tone(self, tone, delay, duty_cycle):
        if isinstance(tone, tuple):
            for t in tone:
                await self._play_one_tone(t, delay/2, duty_cycle)
        else:
            self._tone, freq = self._encode(tone)
            await self._input_stream.put(freq)
            await asyncio.sleep(delay* duty_cycle)
            if duty_cycle != 1:
                await self._input_stream.put(None)
                await asyncio.sleep(delay* (1-duty_cycle))

    @util.mode(force_sync=False)
    async def play(self, song, tempo=120, duty_cycle=.9):
        """Play a sequence of tones

        :param song: tones to be played
        :type song: collections.Iterable
        :param tempo: playback speed, BPM, default is `120` beats/minute
        :type tempo: int
        :param duty_cycle: ratio of the tone duration to the entire beat, 0~1, the default is `0.9`
        :type duty_cycle: float

        .. note::

            This API may change in the future when we come up with a more convenient API to play music

        """

        if not 0< duty_cycle <=1:
            raise ValueError('duty_cycle out of range (0, 1]')
        delay = 60 / tempo
        async with self:
            for tone in song:
                await self._play_one_tone(tone, delay, duty_cycle)
            await self._input_stream.put(None)
            self._tone = None

    '''
    @property
    def input_stream(self):
        """Buzzer input stream

        The input stream must be obtained after the buzzer is turned on, otherwise an exception will be thrown
        """
        if self.closed:
            raise RuntimeError('Buzzer is closed')
        return self._input_stream

    @property
    def raw_input_stream(self):
        return self.input_stream._raw_stream
    '''



    def _encode(self, obj):
        t = Tone(obj) if obj else None
        freq = t.frequency if t else None
        return t, freq
