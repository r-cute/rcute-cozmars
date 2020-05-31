from .util import Component, mode

class Head(Component):
    max_angle = 30
    min_angle = -30

    async def set_angle(self, angle, speed, duration):
        await self.rpc.head(angle, speed, duration)
