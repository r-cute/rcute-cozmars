from . import error, util

class Head(util.Component):
    MAX_ANGLE = 30
    MIN_ANGLE = -30

    async def set_angle(self, angle, speed, duration):
        await self.rpc.head(angle, speed, duration)
