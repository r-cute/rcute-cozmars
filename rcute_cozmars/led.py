from . import util

class LED(util.Component):
    """LED 灯"""

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.default_fade_speed = 2
        """设置 :data:`brightness` 时的默认的渐变速度，默认为 2/s ，若设为 `None` 表示没有渐变"""

    def _light_rpc(self):
        return self._rpc.led

    @property
    def max_brightness(self):
        """最大亮度，`1.0` ，只读"""
        return 1.0

    @property
    def min_brightness(self):
        """最低亮度，即关闭状态，`0.0` ，只读"""
        return .0

    @util.mode(property_type='setter')
    async def brightness(self, *args):
        """亮度，0~1，默认是 `0.05`
        """
        if args:
            await self._light_rpc()(args[0], None, self.default_fade_speed)
        else:
            return round(await self._light_rpc()(), 2)

    @util.mode(force_sync=False)
    async def set_brightness(self, brightness, *, fade_duration=None, fade_speed=None):
        """设置亮度

        :param brightness: 亮度，0~1
        :type brightness: float
        :param fade_duration: 渐变时间（秒） ， 默认是 `None`，表示没有渐变
        :type fade_duration: float
        :param fade_speed: 渐变速度（/秒） ， 默认是 `None`，表示没有渐变
        :type fade_speed: float
        :raises TypeError: 不能同时设置 `fade_duration` 和 `fade_speed` ，否则抛出异常
        """
        if fade_duration and fade_speed:
            raise TypeError('Cannot set both fade_duration and fade_speed')
        await self._light_rpc()(brightness, fade_duration, fade_speed)


