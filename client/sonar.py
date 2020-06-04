from . import error, util

class Sonar(util.Component):
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_in_range = None
        self.when_out_of_range = None

    @util.mode(property_type='setter')
    async def threshold_distance(self, *args):
        return await self.rpc.threshod_distance(*args)

    @util.mode(property_type='setter')
    async def max_distance(self, *args):
        return await self.rpc.max_distance(*args)

    @util.mode(property_type='getter')
    async def distance(self):
        return await self.rpc.distance()
