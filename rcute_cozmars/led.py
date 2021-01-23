from . import util

class LED(util.Component):
    """LED lights"""

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.default_fade_speed = 2
        """The default gradient speed when setting :data:`brightness`, the default is 2/s, if it is set to `None`, it means no gradient"""

    def _light_rpc(self):
        return self._rpc.led

    @property
    def max_brightness(self):
        """Maximum brightness, `1.0`, read only """
        return 1.0

    @property
    def min_brightness(self):
        """Minimum brightness, that is, off state, `0.0`, read only"""
        return .0

    @util.mode(property_type='setter')
    async def brightness(self, *args):
        """Brightness, 0~1, default is `0.05`
        """
        if args:
            await self._light_rpc()(args[0], None, self.default_fade_speed)
        else:
            return round(await self._light_rpc()(), 2)

    @util.mode(force_sync=False)
    async def set_brightness(self, brightness, *, fade_duration=None, fade_speed=None):
        """Set brightness

        :param brightness: brightness, 0~1
        :type brightness: float
        :param fade_duration: fade time (seconds), the default is `None`, which means no fade
        :type fade_duration: float
        :param fade_speed: fade speed (/s), the default is `None`, which means no fade
        :type fade_speed: float
        :raises TypeError: `fade_duration` and `fade_speed` cannot be set at the same time, otherwise an exception will be thrown
        """
        if fade_duration and fade_speed:
            raise TypeError('Cannot set both fade_duration and fade_speed')
        await self._light_rpc()(brightness, fade_duration, fade_speed)
