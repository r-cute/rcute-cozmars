from . import util

class Sonar(util.Component):
    """ Sonar, namely ultrasonic distance sensor
    """
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_in_range = None
        """Callback function, defalts to `None`. Called when the distance to detected obstacle is less than :data:`threshold_distance`.

        The callback function accepts one parameter, which is the distance to detected object, in meters """
        self.when_out_of_range = None
        """Callback function, default to `None`. Called when the distance to the detected obstacle is greater than :data:`threshold_distance`.

        The callback function accepts one parameter, which is the distance to detected object, in meters """

    @util.mode(property_type='getter')
    async def distance(self):
        """Distance to detect obstacles ahead (m)

        When the distance exceeds :data:`max_distance`, it will read :data:`max_distance` """
        return round(await self._rpc.distance(), 2)

    @util.mode(property_type='setter')
    async def max_distance(self, *args):
        """The farthest measurable distance (meters), the default is `0.5` """
        return await self._rpc.max_distance(*args)


    @util.mode(property_type='setter')
    async def threshold_distance(self, *args):
        """Threshold distance (m), default is `0.1`"""
        return await self._rpc.threshod_distance(*args)
