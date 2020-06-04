from . import error, util

class Motors(util.Component):

    @util.mode(property_type='setter')
    async def speed(value=None):
        return await (self.rpc.speed() if value is None else self.rpc.speed(value))

    @util.mode(force_sync=False)
    async def set_speed(value, duration):
        await self.rpc.speed(value, duration)
