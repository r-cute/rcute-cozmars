from . import error, util

class Head(util.Component):
    """头部"""

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.default_speed = None
        """默认的头部转动角速度"""

    @property
    def max_angle(self):
        """最大角度，即最高的仰角，只读
        """
        return 30

    @property
    def min_angle(self):
        """最小角度，即最低的俯视角，只读
        """
        return -30

    @util.mode(property_type='setter')
    async def angle(self, *args):
        """头部的角度"""
        if len(args) >= 1:
            raise error.CozmarsError('Angle accepts at most one parameter')
        return await (self._rpc.head(args[0]) if args else self._rpc.head())

    @util.mode(force_sync=False)
    async def set_angle(self, angle, *, duration=None, speed=None):
        """设置头部的角度

        :param angle: 要设置的头部角度
        :type angle: float
        :param duration: 转动头部的持续时间（秒），默认为 `None` ，表示用最快速度转动
        :type duration: float, optional
        :param speed: 转动头部的角速度（rad/s），默认为 `None` ，表示用最快速度转动
        :type speed: float, optional
        """
        if duration and speed:
            raise error.CozmarsError('Cannot set both duration and speed')
        await self._rpc.head(angle, duration, speed or self.default_speed)

