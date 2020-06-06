import asyncio
from . import error, util
from wsmprpc import RPCStream

class Buzzer(util.StreamComponent):

    def _get_rpc(self):
        self._input_stream = util.SyncAsyncRPCStream(RPCStream(), None if self._mode=='aio' else self._loop)
        return self.rpc.play(request_stream=self._input_stream)

    @util.mode(force_sync=False)
    async def set_tone(self, note, duration=None):
        await self.rpc.tone(str(note), duration)

    @util.mode()
    async def quiet(self):
        await self._close()
        await self.rpc.tone(None, None)

    @util.mode(force_sync=False)
    async def play(self, song):
        async with self:
            for note, delay in song:
                await self._input_stream.put(note)
                await asyncio.sleep(delay/1000)
            await self._input_stream.put(None)

    @property
    def input_stream(self):
        if self.closed:
            raise error.CozmarsError('Buzzer is closed')
        return self._input_stream



