from . import error, util

class Head(util.Component):
    MAX_ANGLE = 30
    MIN_ANGLE = -30

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.default_speed = None

    @util.mode(force_async=False)
    async def set_angle(self, angle, *, duration=None, speed=None):
        await self.rpc.head(angle, duration, speed or self.default_speed)

    @util.mode(property_type='setter')
    async def angle(self, *args):
        if len(args) >= 1:
            raise error.CozmarsError('Angle accepts at most one parameter')
        return await (self.rpc.head(args[0]) if args else self.rpc.head())