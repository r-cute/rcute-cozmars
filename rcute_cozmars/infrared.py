from . import util

class Infrared(util.Component):
    """红外线传感器
    """
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_state_changed = None
        """回调函数，底部任一个红外线传感器的数值变化时调用，默认为 `None`

        该回调函数接受一个参数，即两个红外线传感器的数值组成的 `tuple` """
        self._state = (1, 1)

    @property
    def state(self):
        """底部两个红外线传感器数值组成的一个两元素的 `tuple`，每个元素为 `0` 或者 `1`

        `1` 表示接收到反射，`0` 表示没有接收到反射"""
        return self._state


