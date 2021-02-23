from . import util

class Button(util.Component):
    """ """

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_pressed = None
        """Callback function, called when the button is pressed, the default is `None` """
        self.when_released = None
        """Callback function, called when the button is released, the default is `None` """
        self.when_long_pressed = None
        """Callback function, called when the button is long pressed, the default is `None` """
        self.when_double_pressed = None
        """Callback function, called when the button is double-clicked, the default is `None` """
        self._pressed = False
        self._double_pressed = False
        self._long_pressed = False

    @property
    def pressed(self):
        """ """
        return self._pressed


    @property
    def double_pressed(self):
        """ """
        return self._double_pressed

    @util.mode(property_type='setter')
    async def double_press_threshold(self, *args):
        """Interval threshold between two clicks to be recognized as a double press, in seconds, default is `0.3`"""
        return await self._rpc.double_press_threshold(*args)


    @property
    def long_pressed(self):
        """Whether the button is being long pressed"""
        return self._long_pressed

    @util.mode(property_type='setter')
    async def long_press_threshold(self, *args):
        """The minimum time (in seconds) required to press and hold the button before :data:`when_held` is called, the default is `1.0` """
        return await self._rpc.long_press_threshold(*args)

    @util.mode(property_type='setter')
    async def long_press_repeat(self, *args):
        """Whether to allow repetitive call of :data:`when_long_pressed`, the default is `False`

        If set to `True`, while the button is held down, :data:`when_long_pressed` will be called every :data:`long_press_threshold` """
        return await self._rpc.long_press_repeat(*args)
