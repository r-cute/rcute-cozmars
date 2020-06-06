from . import error, util
from .wsmprpc import RPCStream

class Buzzer(util.InputStreamComponent):

    @util.mode(force_sync=False)
    async def set_tone(self, note, duration=None):
        await self.rpc.tone(str(note), duration)

    @util.mode()
    async def quiet(self):
        await self.close()
        await self.rpc.tone(None, None)

    @util.mode(force_sync=False)
    async def play(self, song):
        async with self:
            for note, delay in song:
                await self._input_stream.put(note)
                await asyncio.sleep(delay/1000)


