import asyncio
from . import util

class Lift(util.Component):
    """手臂
    """

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self._relax_timeout = None
        self.default_speed = 2
        """设置 :data:`height` 时的默认移臂速度（/秒），默认为 `2` ，若设为 `None` 则表示用最快速度移臂"""
        self.auto_relax_delay = 1
        """多长时间内没有动作则自动放松（秒），默认为 `1`，若设为 `None` 则表示不会自动放松

        舵机移动到目标位置后，使其放松能防止长期受力造成损坏，也能节约电池电量
        """

    def _cancel_relax_timeout(self):
        self._relax_timeout and self._relax_timeout.cancel()

    async def _relax_timeout_coro(self):
        await asyncio.sleep(self.auto_relax_delay)
        await self._rpc.relax_lift()

    def _reset_relax_timeout(self):
        if self.auto_relax_delay:
            self._relax_timeout = asyncio.create_task(self._relax_timeout_coro())

    @property
    def max_height(self):
        """移臂最大高度，`1.0` ，只读
        """
        return 1.0

    @property
    def min_height(self):
        """移臂最低高度， `0.0` ，只读
        """
        return 0.0

    @util.mode(property_type='setter')
    async def height(self, *args):
        """臂的高度，0.0~1.0"""
        if len(args) > 1:
            raise TypeError('Height accepts at most one parameter')
        if args:
            self._cancel_relax_timeout()
            await self._rpc.lift(args[0], None, self.default_speed)
            self._reset_relax_timeout()
        else:
            h = await self._rpc.lift()
            return round(h, 2) if h else h

    @util.mode(force_sync=False)
    async def set_height(self, height, *, duration=None, speed=None):
        """设置臂的高度

        :param height: 要设置的臂的高度
        :type height: float
        :param duration: 移动臂的持续时间（秒），默认为 `None` ，表示用最快速度移动
        :type duration: float, optional
        :param speed: 移动臂的速度（/秒），默认为 `None` ，表示用最快速度移动
        :type speed: float, optional
        :raises TypeError: 不能同时设置 `duration` 和 `speed` ，否则抛出异常
        """
        if duration and speed:
            raise TypeError('Cannot set both duration and speed')
        self._cancel_relax_timeout()
        await self._rpc.lift(height, duration, speed)
        self._reset_relax_timeout()

