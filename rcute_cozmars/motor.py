from . import util

class Motor(util.Component):
    """Motor controls the movement of the robot


    .. warning::

        Please be careful not to let the robot fall off the table when moving!

    """

    @util.mode(property_type='setter')
    async def speed(self, value=None):
        """The speed of the motor, the tuple composed of two numbers -1~1 represents the speed of the left and right motors"""
        return await (self._rpc.speed() if value is None else self._rpc.speed(value))

    @util.mode(force_sync=False)
    async def set_speed(self, value, duration=None):
        """Set the speed of the motor, -1~1

        :param value: speed. It can be a number from -1 to 1, which sets the same speed for both motors; it can also be a `tuple` composed of two numbers to set the speed of the left and right motors respectively
        :type value: float / tuple
        :param duration: duration (seconds), the default is `None`, which means that the motor will continue to rotate until :func:`stop` is called or the speed is set to `0`
        :type duration: float
        """
        await self._rpc.speed(value, duration)

    @util.mode()
    async def stop(self):
        """stop
        """
        await self._rpc.speed(0)
