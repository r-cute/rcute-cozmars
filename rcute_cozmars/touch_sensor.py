from . import util

class TouchSensor(util.Component):
    """ """

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_touched = None
        """Callback function, called when the touch sensor is touched, the default is `None` """
        self.when_released = None
        """Callback function, called when the touch sensor is released, the default is `None` """
        self.when_long_touched = None
        """Callback function, called when the touch sensor is long touched, the default is `None` """
        self.when_double_touched = None
        """Callback function, called when the touch sensor is double-clicked, the default is `None` """
        self._touched = False
        self._double_touched = False
        self._long_touched = False

    @property
    def touched(self):
        """ """
        return self._touched

    @property
    def double_touched(self):
        """ """
        return self._double_touched

    @util.mode(property_type='setter')
    async def double_touch_threshold(self, *args):
        """Interval threshold between two clicks to be recognized as a double touch, in seconds, default is `0.3`"""
        return await self._rpc.double_press_threshold(*args)


    @property
    def long_touched(self):
        """Whether the touch sensor is being long touched"""
        return self._long_touched

    @util.mode(property_type='setter')
    async def long_touch_threshold(self, *args):
        """The minimum time (in seconds) required to touch and hold the touch sensor before :data:`when_held` is called, the default is `1.0` """
        return await self._rpc.long_press_threshold(*args)

    @util.mode(property_type='setter')
    async def long_touch_repeat(self, *args):
        """Whether to allow repetitive call of :data:`when_long_touched`, the default is `False`

        If set to `True`, while the touch sensor is held down, :data:`when_long_touched` will be called every :data:`long_touch_threshold` """
        return await self._rpc.long_press_repeat(*args)
