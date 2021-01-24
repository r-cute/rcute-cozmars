from . import util

class Motor(util.Component):
    """


    .. warning::

        Be careful not to drop thr robot off table when it moves!

    """

    @util.mode(property_type='setter')
    async def speed(self, value=None):
        """get/set speed of the motor, the tuple composed of two numbers -1~1 represents the speed of the left and right motors."""
        return await (self._rpc.speed() if value is None else self._rpc.speed(value))

    @util.mode(force_sync=False)
    async def set_speed(self, value, duration=None):
        """

        :param value: -1~1. It can be a number to set speed for both motors, or a two-element tuple to set left and right motors respectively
        :type value: float / tuple
        :param duration: duration in seconds of movement. default is `None` for non-stop until :func:`stop` is called or the speed is set to `0`
        :type duration: float
        """
        await self._rpc.speed(value, duration)

    @util.mode()
    async def stop(self):
        await self._rpc.speed(0)
