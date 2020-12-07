import asyncio
from. import util

class Head(util.Component):
    """head"""

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self._relax_timeout = None
        self.default_speed = 100
        """The default head turning angular velocity (degrees/second) when setting :data:`angle`, the default is `100`, if set to `None`, it means the fastest head turning"""
        self.auto_relax_delay = 1
        """If there is no action for a long time, it will automatically relax (seconds), the default is `1`, if it is set to `None`, it will not automatically relax

        After the steering gear is moved to the target position, it can be relaxed to prevent damage caused by long-term force, and it can also save battery power
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
        """Maximum angle, the highest elevation angle, `30` degree, read only
        """
        return 20

    @property
    def min_angle(self):
        """Minimum angle, that is, the lowest overhead angle, `-30` degrees, read only
        """
        return -20

    @util.mode(property_type='setter')
    async def angle(self, *args):
        """Angle of the head"""
        if len(args)> 1:
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

        :param angle: head angle to be set
        :type angle: float
        :param duration: the duration of turning the head (seconds), the default is `None`, which means turning at the fastest speed
        :type duration: float, optional
        :param speed: the angular speed of turning the head (degrees/second), the default is `None`, which means to rotate at the fastest speed
        :type speed: float, optional
        :raises TypeError: `duration` and `speed` cannot be set at the same time, otherwise an exception will be thrown
        """
        if duration and speed:
            raise TypeError('Cannot set both duration and speed')
        self._cancel_relax_timeout()
        await self._rpc.head(angle, duration, speed)
        self._reset_relax_timeout()