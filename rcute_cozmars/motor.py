from . import util
from . import pair

class _Motor(util.Component):

    @util.mode(property_type='setter')
    async def speed(self, value=None):
        """get/set speed of the motor, the tuple composed of two numbers -1~1 represents the speed of the left and right motors."""
        return self.extract(await self._rpc.speed()) if value is None else (await self._rpc.speed(self.extend(value)))

    @util.mode(force_sync=False)
    async def set_speed(self, value, duration=None):
        """

        :param value: -1~1. It can be a number to set speed for both motors, or a two-element tuple to set left and right motors respectively
        :type value: float / tuple
        :param duration: duration in seconds of movement. default is `None` for non-stop until :func:`stop` is called or the speed is set to `0`
        :type duration: float
        """
        await self._rpc.speed(self.extend(value), duration)

    @util.mode()
    async def stop(self):
        """ """
        await self._rpc.speed(self.extend(0))

class Motor(_Motor, pair.Child):
    def __init__(self, i, robot):
        _Motor.__init__(self, robot)
        pair.Child.__init__(self, i)

class Motors(_Motor, pair.Parent):
    """

    .. warning::

        Be careful not to drop the robot off table when it moves!

    """
    def __init__(self, robot):
        _Motor.__init__(self, robot)
        pair.Parent.__init__(self, Motor, robot)
