from . import error, util

class Lift(util.Component):

    @property
    def max_height(self):
        return 1

    @property
    def min_height(self):
        return 0

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.default_speed = None

    @util.mode(force_sync=False)
    async def set_height(self, height, *, duration=None, speed=None):
        if duration and speed:
            raise error.CozmarsError('Cannot set both duration and speed')
        await self.rpc.lift(height, duration, speed or self.default_speed)

    @util.mode(property_type='setter')
    async def height(self, *args):
        if len(args) >= 1:
            raise error.CozmarsError('Height accepts at most one parameter')
        return await (self.rpc.lift(args[0]) if args else self.rpc.lift())
