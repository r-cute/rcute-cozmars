from . import util

class Button(util.Component):
    """按钮
    """
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_pressed = None
        """回调函数，当按钮被按下时调用，默认为 `None` """
        self.when_released = None
        """回调函数，当按钮被松开时调用，默认为 `None` """
        self.when_held = None
        """回调函数，当按钮被长按时调用，默认为 `None` """
        self.when_double_pressed = None
        """回调函数，当按钮被双击时调用，默认为 `None` """
        self._pressed = False
        self._double_pressed = False
        self._held = False

    @property
    def pressed(self):
        """按钮是否被按下"""
        return self._pressed


    @property
    def double_pressed(self):
        """按钮是否被双击"""
        return self._double_pressed

    @util.mode(property_type='setter')
    async def double_press_max_interval(self, *args):
        """双击间隔最长时间（秒），默认为 `0.3`

        如果两次单击时间超过这个时间则不会被认定为双击"""
        return await self._rpc.double_press_max_interval(*args)


    @property
    def held(self):
        """按钮是否被长按"""
        return self._held

    @util.mode(property_type='setter')
    async def hold_time(self, *args):
        """长按按钮所需的最短时间（秒），默认为 `1.0`

        按钮持续被按住超过这个时长则会调用 :data:`when_held` """
        return await self._rpc.hold_time(*args)

    @util.mode(property_type='setter')
    async def hold_repeat(self, *args):
        """是否允许连续连续调用 :data:`when_held` ，默认为 `False`

        若设为 `True` ，则按钮被持续按住时，每隔 :data:`hold_time` 时间就会调用一次 :data:`when_held` """
        return await self._rpc.hold_repeat(*args)

