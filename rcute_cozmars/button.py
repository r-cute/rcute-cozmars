from. import util

class Button(util.Component):
    """ button
    """
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_pressed = None
        """Callback function, called when the button is pressed, the default is `None` """
        self.when_released = None
        """Callback function, called when the button is released, the default is `None` """
        self.when_held = None
        """Callback function, called when the button is long pressed, the default is `None` """
        self.when_double_pressed = None
        """Callback function, called when the button is double-clicked, the default is `None` """
        self._pressed = False
        self._double_pressed = False
        self._held = False

    @property
    def pressed(self):
        """ Whether the button is pressed"""
        return self._pressed

    @property
    def double_pressed(self):
        """Button is double-clicked"""
        return self._double_pressed

    @util.mode(property_type='setter')
    async def double_press_max_interval(self, *args):
        """Maximum time between double-clicks (seconds), default is `0.3`

        If the time of two clicks exceeds this time, it will not be recognized as double click """
        return await self._rpc.double_press_max_interval(*args)


    @property
    def held(self):
        """Whether the button has been long pressed"""
        return self._held

    @util.mode(property_type='setter')
    async def hold_time(self, *args):
        """The minimum time (seconds) required to press and hold the button, the default is `1.0`

        If the button is held for longer than this time, it will call :data:`when_held` """
        return await self._rpc.hold_time(*args)

    @util.mode(property_type='setter')
    async def hold_repeat(self, *args):
        """Whether to allow continuous continuous calling :data:`when_held`, the default is `False`

        If set to `True`, when the button is held down, it will be called every :data:`hold_time` time :data:`when_held` """
        return await self._rpc.hold_repeat(*args)