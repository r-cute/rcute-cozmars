from. import util

class Sonar(util.Component):
    """ Sonar, which is an ultrasonic distance sensor
    """
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_in_range = None
        """Callback function, called when the distance of detecting the obstacle ahead is less than the threshold distance :data:`threshold_distance`, the default is `None`

        The callback function accepts one parameter, which is the distance (meters) detected at this time """
        self.when_out_of_range = None
        """Callback function, which is called when the distance to the front obstacle is greater than the threshold distance :data:`threshold_distance`, the default is `None`

        The callback function accepts one parameter, which is the distance (meters) detected at this time """

    @util.mode(property_type='getter')
    async def distance(self):
        """Distance to detect obstacles ahead (m)

        When the distance exceeds :data:`max_distance`, it can only display :data:`max_distance` """
        return round(await self._rpc.distance(), 2)

    @util.mode(property_type='setter')
    async def max_distance(self, *args):
        """The farthest measurable distance (meters), the default is `0.5` """
        return await self._rpc.max_distance(*args)


    @util.mode(property_type='setter')
    async def threshold_distance(self, *args):
        """Threshold distance (m), default is `0.1`

        Triggered when the distance to the front obstacle is less than the threshold distance:data:`when_in_range` time, trigger when the distance is greater than the threshold :data:`when_out_of_range` event """
        return await self._rpc.threshod_distance(*args)