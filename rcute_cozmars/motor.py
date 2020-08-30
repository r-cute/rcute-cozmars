from . import util

class Motor(util.Component):
    """马达，控制机器人的移动


    .. warning::

        移动的时候请小心别让机器人从桌上掉下来！

    """

    @util.mode(property_type='setter')
    async def speed(self, value=None):
        """马达的速度，两个 -1~1 的数组成的 `tuple` 表示左右马达的速度"""
        return await (self._rpc.speed() if value is None else self._rpc.speed(value))

    @util.mode(force_sync=False)
    async def set_speed(self, value, duration=None):
        """设置马达的速度，-1~1

        :param value: 速度。可以是一个 -1~1 的数，为两个马达都会设置相同的速度；也可以是两个数组成的 `tuple`，分别设置左右马达的速度
        :type value: float / tuple
        :param duration: 持续时间（秒），默认是 `None` ，表示让马达持续转动直到调用 :func:`stop` 或将速度设为 `0`
        :type duration: float
        """
        await self._rpc.speed(value, duration)

    @util.mode()
    async def stop(self):
        """停止
        """
        await self._rpc.speed(0)
