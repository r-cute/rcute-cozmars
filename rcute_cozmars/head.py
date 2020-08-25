import asyncio
from . import util

class Head(util.Component):
    """头部"""

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self._relax_timeout = None
        self.default_speed = 100
        """设置 :data:`angle` 时的默认的头部转动角速度（度/秒），默认为 `100` ，若设为 `None` 则表示用最快转头"""
        self.auto_relax_delay = 1
        """多长时间内没有动作则自动放松（秒），默认为 `1`，若设为 `None` 则表示不会自动放松

        舵机移动到目标位置后，使其放松能防止长期受力造成损坏，也能节约电池电量
        """

    def _cancel_relax_timeout(self):
        self._relax_timeout and self._relax_timeout.cancel()

    async def _relax_timeout_coro(self):
        await asyncio.sleep(self.auto_relax_delay)
        await self._rpc.relax_head()

    def _reset_relax_timeout(self):
        if self.auto_relax_delay:
            self._relax_timeout = asyncio.create_task(self._relax_timeout_coro())

    @property
    def max_angle(self):
        """最大角度，即最高的仰角， `30` 度，只读
        """
        return 30

    @property
    def min_angle(self):
        """最小角度，即最低的俯视角， `-30` 度，只读
        """
        return -30

    @util.mode(property_type='setter')
    async def angle(self, *args):
        """头部的角度"""
        if len(args) > 1:
            raise TypeError('Angle accepts at most one parameter')
        if args:
            self._cancel_relax_timeout()
            await self._rpc.head(args[0], None, self.default_speed)
            self._reset_relax_timeout()
        else:
            a = await self._rpc.head()
            return round(a, 2) if a else a

    @util.mode(force_sync=False)
    async def set_angle(self, angle, *, duration=None, speed=None):
        """设置头部的角度

        :param angle: 要设置的头部角度
        :type angle: float
        :param duration: 转动头部的持续时间（秒），默认为 `None` ，表示用最快速度转动
        :type duration: float, optional
        :param speed: 转动头部的角速度（度/秒），默认为 `None` ，表示用最快速度转动
        :type speed: float, optional
        :raises TypeError: 不能同时设置 `duration` 和 `speed` ，否则抛出异常
        """
        if duration and speed:
            raise TypeError('Cannot set both duration and speed')
        self._cancel_relax_timeout()
        await self._rpc.head(angle, duration, speed)
        self._reset_relax_timeout()

