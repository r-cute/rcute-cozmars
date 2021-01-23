import asyncio
from . import util

class Head(util.Component):
    """head"""

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self._relax_timeout = None
        self.default_speed = 100
        """The default head rotation angular velocity (degrees/second), the default is `100`, if set to `None`, it will rotate at fastest speed"""
        self.auto_relax_delay = 1
        """time delay to automatically relax servo after head rotates, default to 1 sec. If set to `None`, servo will not relax.

        When head moves to target position, relaxing the servo can prevent damage and save battery power.
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
        """30 degrees, read only
        """
        return 30

    @property
    def min_angle(self):
        """-30 degrees, read only
        """
        return -30

    @util.mode(property_type='setter')
    async def angle(self, *args):
        """get/set target angle at :data:`default_speed`"""
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
        """Set the angle of the head

        :param angle: target angle position
        :type angle: float
        :param duration: duration in seconds for the movement, default is `None` for fastest speed
        :type duration: float, optional
        :param speed: angular speed at which to move head, the default is `None` for fastest speed
        :type speed: float, optional
        :raises TypeError: `duration` and `speed` cannot both be set, otherwise an exception will be thrown
        """
        if duration and speed:
            raise TypeError('Cannot set both duration and speed')
        self._cancel_relax_timeout()
        await self._rpc.head(angle, duration, speed)
        self._reset_relax_timeout()
