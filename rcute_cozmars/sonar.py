from . import util

class Sonar(util.Component):
    """声纳，即超声波距离传感器
    """
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_in_range = None
        """回调函数，当探测到前方障碍物的距离小于阈值距离 :data:`threshold_distance` 时调用，默认为 `None`

        该回调函数接受一个参数，即此时探测到的前方距离（米）"""
        self.when_out_of_range = None
        """回调函数，当探测到前方障碍物的距离大于阈值距离 :data:`threshold_distance` 时调用，默认为 `None`

        该回调函数接受一个参数，即此时探测到的前方距离（米）"""

    @util.mode(property_type='getter')
    async def distance(self):
        """探测到前方障碍物的距离（米）

        当距离超过 :data:`max_distance` 时只能也只显示 :data:`max_distance` """
        return round(await self._rpc.distance(), 2)

    @util.mode(property_type='setter')
    async def max_distance(self, *args):
        """最远能测量的距离（米），默认是 `0.5` """
        return await self._rpc.max_distance(*args)


    @util.mode(property_type='setter')
    async def threshold_distance(self, *args):
        """阈值距离（米），默认时 `0.1`

        当探测到前方障碍物的距离小于阈值距离时触发 :data:`when_in_range` 时间，大于阈值距离时触发 :data:`when_out_of_range` 事件 """
        return await self._rpc.threshod_distance(*args)



