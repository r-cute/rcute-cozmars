from . import error, util

class Sonar(util.Component):
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_in_range = None
        self.when_out_of_range = None

    @util.get_set
    @util.mode()
    async def threshold_distance(self, *args):
        return await self.rpc.threshod_distance(*args)

    @util.get_set
    @util.mode()
    async def max_distance(self, *args):
        return await self.rpc.max_distance(*args)

    @util.get
    @util.mode()
    async def distance(self):
        return await self.rpc.distance()
