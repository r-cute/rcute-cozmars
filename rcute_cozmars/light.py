from . import util
from . import pair
from . import led

class _Light(led.LED):
    async def _brightness(self, *args):
        if args:
            await self._rpc._led_brightness(self.extend(args[0]), *args[1:])
        else:
            return self.extract(await self._rpc._led_brightness())

    def _light_rpc(self):
        return self._brightness

    @util.mode(property_type='setter')
    async def color(self, c=None):
        """get/set led color in BGR mode"""
        return self.extract(await self._rpc.led_color()) if c is None else (await self._rpc.led_color(self.extend(c)))

class Light(_Light, pair.Child):
    def __init__(self, i, robot):
        _Light.__init__(self, robot)
        pair.ChildComponent.__init__(i)

class Lights(_Light, pair.Parent):
    """Builtin LEDs on the sonar module"""
    def __init__(self, robot):
        _Light.__init__(self, robot)
        pair.ParentComponent.__init__(self, Light, robot)
