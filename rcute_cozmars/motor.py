from . import error, util

class Motor(util.Component):

    @util.mode(property_type='setter')
    async def speed(self, value=None):
        """motor speed"""
        return await (self._rpc.speed() if value is None else self._rpc.speed(value))

    @util.mode(force_sync=False)
    async def set_speed(self, value, duration):
        await self._rpc.speed(value, duration)
