import asyncio
from . import util

class Lift(util.Component):
    """Arm
    """

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self._relax_timeout = None
        self.default_speed = 2
        """The default arm moving speed (/sec) when setting :data:`height`, the default is `2`, if it is set to `None`, it means moving the arm at the fastest speed"""
        self.auto_relax_delay = 1
        """If there is no action for a long time, it will automatically relax (seconds), the default is `1`, if it is set to `None`, it means that it will not automatically relax

        After the steering gear is moved to the target position, it can be relaxed to prevent damage caused by long-term force, and it can also save battery power
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
        """Maximum height of moving arm, `1.0`, read only
        """
        return 1.0

    @property
    def min_height(self):
        """Minimum height of arm moving, `0.0`, read only
        """
        return 0.0

    @util.mode(property_type='setter')
    async def height(self, *args):
        """The height of the arm, 0.0~1.0"""
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
        """Set the height of the arm

        :param height: the height of the arm to be set
        :type height: float
        :param duration: the duration of the moving arm (seconds), the default is `None`, which means to move at the fastest speed
        :type duration: float, optional
        :param speed: the speed of the moving arm (/s), the default is `None`, which means to move at the fastest speed
        :type speed: float, optional
        :raises TypeError: `duration` and `speed` cannot be set at the same time, otherwise an exception will be thrown
        """
        if duration and speed:
            raise TypeError('Cannot set both duration and speed')
        self._cancel_relax_timeout()
        await self._rpc.lift(height, duration, speed)
        self._reset_relax_timeout()
