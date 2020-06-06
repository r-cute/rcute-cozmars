from . import error, util

class Buzzer(util.Component):

    @util.mode(force_sync=False)
    async def set_tone(self, note, duration=None):
        await self.rpc.tone(note, duration)

    @util.mode()
    async def stop(self):
        await self.rpc.tone(None, None)

    @util.mode(force_sync=False)
    async def play(self):
        pass