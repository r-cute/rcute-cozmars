import asyncio
from . import util

class Lift(util.Component):
    """Arm
    """

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self._relax_timeout = None
        self.default_speed = 2
        """The default lift moving speed, the default is 2/s, if set to `None`, it will move at fastest speed"""
        self.auto_relax_delay = 1
        """time delay to automatically relax servo after lift moves, default to 1 sec. If set to `None`, servo will not relax.

        When lift moves to target position, relaxing the servo can prevent damage and save battery power.
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
        """ `1.0`, read only
        """
        return 1.0

    @property
    def min_height(self):
        """ `0.0`, read only
        """
        return 0.0

    @util.mode(property_type='setter')
    async def height(self, *args):
        """get/set lift height at :data:`default_speed`, 0.0~1.0"""
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
        """

        :param height: target height position
        :type height: float
        :param duration: duration of movement, default is `None` for fastest speed
        :type duration: float, optional
        :param speed: (/s), default is `None` for fastest speed
        :type speed: float, optional
        :raises TypeError: `duration` and `speed` cannot both be set, otherwise an exception will be thrown
        """
        if duration and speed:
            raise TypeError('Cannot set both duration and speed')
        self._cancel_relax_timeout()
        await self._rpc.lift(height, duration, speed)
        self._reset_relax_timeout()
